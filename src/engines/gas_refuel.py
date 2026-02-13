"""Gas refuel engine using AVNU swap (ETH->STRK) for StarkNet accounts."""
from __future__ import annotations

import os
import sys
import requests
from typing import Dict, Any, Optional, List

from rich.console import Console
from rich.panel import Panel
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models import StarknetChainId
from starknet_py.net.client_models import Call
from starknet_py.hash.selector import get_selector_from_name

from ..foundation.constants import STARKNET_ETH_CONTRACT
from ..foundation.network import NetworkOracle
from ..foundation.security import SecurityManager

console = Console()


class GasRefuelEngine:
    def __init__(self, network_oracle: NetworkOracle, security_manager: SecurityManager):
        self.network_oracle = network_oracle
        self.security_manager = security_manager

    async def _ensure_init(self) -> bool:
        if not self.network_oracle.is_initialized:
            if not await self.network_oracle.initialize():
                return False
        if not await self.security_manager.initialize():
            return False
        if not self.security_manager.is_vault_unlocked():
            await self.security_manager.unlock_vault_auto()
        return True

    def get_swap_quote(self, amount_eth: float = 0.002) -> Optional[Dict[str, Any]]:
        url = "https://starknet.api.avnu.fi/swap/v1/quotes"
        eth_address = int(os.getenv("STARKNET_ETH_CONTRACT", STARKNET_ETH_CONTRACT), 16)
        strk_address = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
        amount_hex = hex(int(amount_eth * 10**18))

        params = {
            "sellTokenAddress": hex(eth_address),
            "buyTokenAddress": strk_address,
            "sellAmount": amount_hex,
            "size": 1,
        }

        console.print(f"[blue]🔍 Fetching AVNU quote: {amount_eth} ETH -> STRK...[/blue]")
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                quotes = response.json()
                if quotes:
                    quote = quotes[0]
                    buy_amount = int(quote["buyAmount"], 16) / 10**18
                    sell_amount = int(quote["sellAmount"], 16) / 10**18
                    console.print(
                        Panel.fit(
                            f"[bold green]✅ Quote Received[/bold green]\n\n"
                            f"Sell: [yellow]{sell_amount:.6f} ETH[/yellow]\n"
                            f"Buy: [bold green]{buy_amount:.6f} STRK[/bold green]\n"
                            f"Quote ID: [dim]{quote['quoteId']}[/dim]",
                            title="AVNU Swap Quote",
                        )
                    )
                    return quote
                console.print("[yellow]⚠ No quotes found for this pair.[/yellow]")
            else:
                console.print(f"[red]❌ AVNU API Error: {response.status_code} - {response.text}[/red]")
        except Exception as e:
            console.print(f"[red]❌ Connection Error: {e}[/red]")
        return None

    async def execute_swap(self, quote: Dict[str, Any], confirm: bool = False) -> Dict[str, Any]:
        if not await self._ensure_init():
            return {"success": False, "error": "Initialization failed"}

        wallet_addr = os.getenv("STARKNET_WALLET_ADDRESS")
        rpc_client: FullNodeClient = self.network_oracle.clients.get("starknet")
        priv_key_hex = await self.security_manager.get_starknet_private_key()

        if not all([wallet_addr, rpc_client, priv_key_hex]):
            return {"success": False, "error": "Missing wallet, client, or private key"}

        # Build swap transaction
        build_url = "https://starknet.api.avnu.fi/swap/v1/build"
        payload = {"quoteId": quote["quoteId"], "takerAddress": wallet_addr, "slippage": 0.01}

        console.print("[blue]🛠 Building swap transaction...[/blue]")
        res = requests.post(build_url, json=payload)
        build_data = res.json()
        if res.status_code != 200:
            return {"success": False, "error": f"Build Error: {res.status_code} - {build_data}"}

        calls: List[Call] = []
        if "calls" in build_data:
            for call in build_data["calls"]:
                calls.append(
                    Call(
                        to_addr=int(call["contractAddress"], 16),
                        selector=int(call["entrypoint"], 16)
                        if isinstance(call["entrypoint"], str) and call["entrypoint"].startswith("0x")
                        else call["entrypoint"],
                        calldata=[int(x, 16) for x in call["calldata"]],
                    )
                )
        elif "contractAddress" in build_data:
            calls.append(
                Call(
                    to_addr=int(build_data["contractAddress"], 16),
                    selector=int(build_data["entrypoint"], 16)
                    if isinstance(build_data["entrypoint"], str) and build_data["entrypoint"].startswith("0x")
                    else build_data["entrypoint"],
                    calldata=[int(x, 16) for x in build_data["calldata"]],
                )
            )

        if not calls:
            return {"success": False, "error": "No calls found in build data"}

        # Fix entrypoint names
        if "calls" in build_data:
            for i, call in enumerate(calls):
                orig_call = build_data["calls"][i]
                if isinstance(orig_call["entrypoint"], str) and not orig_call["entrypoint"].startswith("0x"):
                    calls[i] = Call(
                        to_addr=call.to_addr,
                        selector=get_selector_from_name(orig_call["entrypoint"]),
                        calldata=call.calldata,
                    )
        else:
            orig_call = build_data
            if isinstance(orig_call["entrypoint"], str) and not orig_call["entrypoint"].startswith("0x"):
                calls[0] = Call(
                    to_addr=calls[0].to_addr,
                    selector=get_selector_from_name(orig_call["entrypoint"]),
                    calldata=calls[0].calldata,
                )

        if not confirm:
            return {"success": True, "dry_run": True, "calls": len(calls)}

        try:
            key_pair = KeyPair.from_private_key(int(priv_key_hex, 16))
            account = Account(address=wallet_addr, client=rpc_client, key_pair=key_pair, chain=StarknetChainId.MAINNET)
            invoke_tx = await account.execute_v3(calls=calls, auto_estimate=True)
            return {"success": True, "tx_hash": hex(invoke_tx.transaction_hash)}
        except Exception as e:
            return {"success": False, "error": str(e)}
