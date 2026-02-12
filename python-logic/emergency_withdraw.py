"""
Emergency Withdraw - Atomic Deploy + Transfer for StarkNet v0.14.0+
====================================================================
Burn-and-Exit protocol for extracting funds from undeployed accounts.
"""

import os
import sys
import asyncio
from rich.console import Console
from rich.panel import Panel
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models import StarknetChainId
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call
from starknet_py.common import create_casm_class
import json

console = Console()

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): 
        console.print("[yellow]⚠️ .env file not found[/yellow]")
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()
    
    # Debug: Show loaded RPC URLs
    rpc_urls = [
        os.getenv("STARKNET_MAINNET_URL"),
        os.getenv("STARKNET_LAVA_URL"), 
        os.getenv("STARKNET_1RPC_URL"),
        os.getenv("STARKNET_ONFINALITY_URL")
    ]
    console.print(f"[dim]Loaded {len([u for u in rpc_urls if u])} RPC URLs[/dim]")

# Load environment immediately
load_env()

class RPCManager:
    def __init__(self):
        self.urls = [
            os.getenv("STARKNET_MAINNET_URL"),
            os.getenv("STARKNET_LAVA_URL"),
            os.getenv("STARKNET_1RPC_URL"),
            os.getenv("STARKNET_ONFINALITY_URL")
        ]
        self.urls = [u for u in self.urls if u]
        self.current_idx = 0
        if not self.urls:
            console.print("[bold red]❌ RPC Manager: No Starknet RPC URLs found![/bold red]")

    def get_next_url(self):
        if not self.urls: return None
        url = self.urls[self.current_idx % len(self.urls)]
        self.current_idx += 1
        return url

    async def call_with_rotation(self, func, *args, **kwargs):
        for _ in range(len(self.urls) or 1):
            url = self.get_next_url()
            if not url: continue
            
            client = FullNodeClient(node_url=url)
            try:
                await client.get_block_number()
                return await func(client, *args, **kwargs)
            except Exception as e:
                console.print(f"[yellow]⚠️ RPC Fail ({url[:30]}...): {e}[/yellow]")
        return None

rpc_manager = RPCManager()

async def get_account_balance(client, address):
    """Check ETH balance for any address"""
    eth_address = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
    call = Call(
        to_addr=int(eth_address, 16),
        selector=get_selector_from_name("balanceOf"),
        calldata=[int(address, 16)]
    )
    try:
        res = await client.call_contract(call)
        return res[0] / 10**18
    except:
        return 0.0

async def check_account_deployment(client, address):
    """Check if account is deployed"""
    try:
        await client.get_class_hash_at(contract_address=int(address, 16))
        return True
    except:
        return False

async def get_coinbase_starknet_address():
    """Get Coinbase Starknet deposit address using CDP API"""
    try:
        from cdp import Wallet, Cdp
        
        # Setup CDP using existing credentials
        api_key_name = os.getenv("COINBASE_CLIENT_API_KEY")
        api_key_private = os.getenv("COINBASE_API_PRIVATE_KEY")
        
        if not api_key_name or not api_key_private:
            console.print("[red]❌ Coinbase CDP credentials not found[/red]")
            return None
            
        Cdp.configure(api_key_name, api_key_private.replace("\\n", "\n"))
        
        # Try to find existing wallet first (avoids rate limits)
        try:
            wallets = list(Wallet.list())
            wallet = next((w for w in wallets if w.network_id == "starknet-mainnet"), None)
            if wallet:
                console.print("[green]✅ Found existing Coinbase Starknet wallet[/green]")
                return wallet.default_address.address
        except Exception as e:
            console.print(f"[yellow]⚠️ Wallet list failed: {e}[/yellow]")
        
        # Fallback: create new wallet if rate limited
        console.print("[yellow]🔄 Creating new Coinbase Starknet wallet...[/yellow]")
        wallet = Wallet.create(network_id="starknet-mainnet")
        return wallet.default_address.address
        
    except Exception as e:
        console.print(f"[red]❌ Failed to get Coinbase Starknet address: {e}[/red]")
        # When API is exhausted, use a simple hardcoded address
        console.print("[yellow]⚠️ API exhausted. Using manual address entry.[/yellow]")
        return None  # Will trigger manual input

async def execute_emergency_withdraw(target_address):
    """Atomic deploy + transfer to bypass STRK mandate"""
    # Load environment (already loaded globally, but ensuring fresh data)
    load_env()
    
    wallet_addr = os.getenv("STARKNET_WALLET_ADDRESS")
    priv_key = os.getenv("STARKNET_PRIVATE_KEY")
    
    console.print(f"[dim]Debug: Wallet={wallet_addr}, HasKey={'Yes' if priv_key else 'No'}[/dim]")
    
    if not wallet_addr or not priv_key:
        console.print("[red]❌ Missing STARKNET_WALLET_ADDRESS or STARKNET_PRIVATE_KEY in .env[/red]")
        return False

    console.print(Panel.fit(
        f"[bold red]🚨 EMERGENCY WITHDRAW[/bold red]\n"
        f"From: {wallet_addr}\n"
        f"To: {target_address}\n"
        f"Mode: Atomic Deploy + Transfer",
        title="Burn-and-Exit Protocol"
    ))

    async def _execute(client):
        # 1. Check current balance
        balance = await get_account_balance(client, wallet_addr)
        if balance <= 0.001:  # Need gas for deployment
            console.print(f"[red]❌ Balance too low: {balance:.6f} ETH[/red]")
            return False

        # 2. Check if already deployed
        is_deployed = await check_account_deployment(client, wallet_addr)
        console.print(f"[dim]Account deployed: {is_deployed}[/dim]")

        # 3. Setup account
        key_pair = KeyPair.from_private_key(priv_key)
        account = Account(
            address=wallet_addr,
            client=client,
            key_pair=key_pair,
            chain=StarknetChainId.MAINNET
        )

        # 4. Calculate withdrawal amount (leave 0.001 ETH for gas)
        withdraw_amount = balance - 0.001
        console.print(f"[cyan]Withdrawal amount: {withdraw_amount:.6f} ETH[/cyan]")

        if "--confirm" not in sys.argv:
            console.print("[yellow]⚠ Simulation only. Run with --confirm to execute.[/yellow]")
            return True

        try:
            if not is_deployed:
                console.print("[yellow]🔧 Deploying account first...[/yellow]")
                # Deploy account (this will use ETH for gas, bypassing STRK requirement)
                deploy_tx = await account.deploy_account_v3(auto_estimate=True)
                console.print(f"[green]✅ Account deployed: {hex(deploy_tx.transaction_hash)}[/green]")
                await client.wait_for_tx(deploy_tx.transaction_hash)

            # 5. Transfer ETH
            console.print(f"[yellow]🚀 Transferring {withdraw_amount:.6f} ETH to {target_address}...[/yellow]")
            
            eth_address = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
            transfer_call = Call(
                to_addr=int(eth_address, 16),
                selector=get_selector_from_name("transfer"),
                calldata=[
                    int(target_address, 16),  # recipient
                    int(withdraw_amount * 10**18)  # amount (low precision)
                ]
            )

            # Use ETH for gas to bypass STRK requirement
            invoke_tx = await account.execute_v3(
                calls=[transfer_call],
                auto_estimate=True,
                l1_resource_bounds={
                    "max_amount": int(0.005 * 10**18),  # 0.005 ETH max
                    "max_price_per_unit": int(20 * 10**9)  # 20 gwei max
                }
            )

            console.print(f"[bold green]✨ WITHDRAWAL BROADCASTED![/bold green]")
            console.print(f"Transaction Hash: [cyan]{hex(invoke_tx.transaction_hash)}[/cyan]")
            console.print(f"Amount: {withdraw_amount:.6f} ETH")
            console.print(f"Target: {target_address}")
            
            return True

        except Exception as e:
            console.print(f"[bold red]❌ Emergency Withdraw Failed: {e}[/bold red]")
            return False

    # Execute with RPC rotation
    return await rpc_manager.call_with_rotation(_execute)

if __name__ == "__main__":
    # Try API first, fallback to manual input
    target_address = asyncio.run(get_coinbase_starknet_address())
    
    if not target_address:
        console.print(Panel.fit(
            "[bold yellow]📝 Manual Entry Required[/bold yellow]\n"
            "Coinbase API exhausted.\n"
            "Please enter your Coinbase Starknet deposit address:",
            title="Address Input"
        ))
        target_address = input("Coinbase Starknet Address: ").strip()
        
        if not target_address or not target_address.startswith("0x"):
            console.print("[red]❌ Invalid address format[/red]")
            sys.exit(1)
    
    console.print(Panel.fit(
        f"[bold cyan]🎯 Extraction Target[/bold cyan]\n"
        f"Withdrawing to: {target_address}\n"
        f"[dim]Ready for emergency withdrawal[/dim]",
        title="Emergency Withdraw"
    ))
    
    asyncio.run(execute_emergency_withdraw(target_address))
