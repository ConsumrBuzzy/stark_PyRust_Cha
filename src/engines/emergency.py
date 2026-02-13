"""Emergency withdrawal engine: deploy + transfer using ETH to bypass STRK requirement."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional

from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.full_node_client import FullNodeClient

from ..foundation.constants import STARKNET_ETH_CONTRACT
from ..foundation.security import SecurityManager
from ..foundation.network import NetworkOracle


@dataclass
class EmergencyWithdrawResult:
    success: bool
    message: str
    tx_hash: Optional[str] = None
    amount_eth: Optional[float] = None
    target_address: Optional[str] = None
    dry_run: bool = False
    deployed: Optional[bool] = None
    balance_eth: Optional[float] = None


class EmergencyWithdrawEngine:
    """Handles atomic deploy + transfer for undeployed accounts."""

    def __init__(self, network_oracle: NetworkOracle, security_manager: SecurityManager):
        self.network_oracle = network_oracle
        self.security_manager = security_manager

    async def _get_balance(self, client: FullNodeClient, address: str) -> float:
        call = Call(
            to_addr=int(STARKNET_ETH_CONTRACT, 16),
            selector=get_selector_from_name("balanceOf"),
            calldata=[int(address, 16)],
        )
        try:
            res = await client.call_contract(call)
            return res[0] / 1e18
        except Exception:
            return 0.0

    async def _is_deployed(self, client: FullNodeClient, address: str) -> bool:
        try:
            await client.get_class_hash_at(contract_address=int(address, 16))
            return True
        except Exception:
            return False

    async def execute(self, target_address: str, confirm: bool = False) -> EmergencyWithdrawResult:
        # Ensure network and security are initialized
        if not self.network_oracle.is_initialized:
            ok = await self.network_oracle.initialize()
            if not ok:
                return EmergencyWithdrawResult(False, "Network initialization failed")

        if not await self.security_manager.initialize():
            return EmergencyWithdrawResult(False, "Security manager initialization failed")

        # Attempt auto unlock if vault locked
        if not self.security_manager.is_vault_unlocked():
            await self.security_manager.unlock_vault_auto()

        wallet_addr = os.getenv("STARKNET_WALLET_ADDRESS")
        if not wallet_addr:
            return EmergencyWithdrawResult(False, "STARKNET_WALLET_ADDRESS missing in environment")

        priv_key = await self.security_manager.get_starknet_private_key()
        if not priv_key:
            return EmergencyWithdrawResult(False, "StarkNet private key unavailable (unlock vault or set env)")

        client: FullNodeClient = self.network_oracle.clients.get("starknet")
        if not client:
            return EmergencyWithdrawResult(False, "StarkNet client unavailable")

        balance = await self._get_balance(client, wallet_addr)
        is_deployed = await self._is_deployed(client, wallet_addr)

        if balance <= 0.001:
            return EmergencyWithdrawResult(False, f"Balance too low: {balance:.6f} ETH", deployed=is_deployed, balance_eth=balance)

        withdraw_amount = balance - 0.001

        if not confirm:
            return EmergencyWithdrawResult(
                True,
                "Simulation only (use confirm to execute)",
                dry_run=True,
                deployed=is_deployed,
                balance_eth=balance,
                amount_eth=withdraw_amount,
                target_address=target_address,
            )

        if not is_deployed:
            return EmergencyWithdrawResult(False, "Account not deployed; deploy before withdrawing", deployed=False, balance_eth=balance)

        try:
            key_pair = KeyPair.from_private_key(int(priv_key, 16))
            account = Account(
                address=wallet_addr,
                client=client,
                key_pair=key_pair,
                chain=self.network_oracle.networks["starknet"].chain_id,
            )

            transfer_call = Call(
                to_addr=int(STARKNET_ETH_CONTRACT, 16),
                selector=get_selector_from_name("transfer"),
                calldata=[int(target_address, 16), int(withdraw_amount * 10**18)],
            )

            invoke_tx = await account.execute_v3(calls=[transfer_call], auto_estimate=True)

            return EmergencyWithdrawResult(
                True,
                "Withdrawal broadcasted",
                tx_hash=hex(invoke_tx.transaction_hash),
                amount_eth=withdraw_amount,
                target_address=target_address,
                deployed=is_deployed,
                balance_eth=balance,
            )
        except Exception as e:
            return EmergencyWithdrawResult(False, f"Emergency withdraw failed: {e}", deployed=is_deployed, balance_eth=balance)
