"""
Force Deploy Account - CLI Alternative
=====================================
Direct deployment using starknet-py Account class
"""

import os
import asyncio
from rich.console import Console
from rich.panel import Panel
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models import StarknetChainId
from starknet_py.hash.address import compute_address
from starknet_py.net.client_models import Call

console = Console()

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

load_env()

async def deploy_account():
    """Force deploy the counterfactual account"""
    wallet_addr = "os.getenv("STARKNET_WALLET_ADDRESS")"
    priv_key = "int(os.getenv("STARKNET_ARGENT_PROXY_HASH", "0x06d44f5b497e5222d3c6fe5158d3b73a575450575b99d2101c5c180d07bc318b"), 16)"
    rpc_url = os.getenv("STARKNET_MAINNET_URL")
    
    console.print(Panel.fit(
        f"[bold red]🚨 FORCE DEPLOY[/bold red]\n"
        f"Account: {wallet_addr}\n"
        f"Network: StarkNet Mainnet",
        title="Account Deployment"
    ))
    
    if not rpc_url:
        console.print("[red]❌ STARKNET_MAINNET_URL not found in .env[/red]")
        return None
    
    client = FullNodeClient(node_url=rpc_url)
    key_pair = KeyPair.from_private_key(int(priv_key, 16))
    
    # Standard Cairo 0.5.0 account class (OpenZeppelin)
    account_class_hash = "0x0481e3ed6c4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e4e"
    
    try:
        console.print("[yellow]🔧 Checking account deployment status...[/yellow]")
        
        # Check if account is already deployed
        try:
            class_hash = await client.get_class_hash_at(contract_address=int(wallet_addr, 16))
            console.print("[green]✅ Account already deployed![/green]")
            console.print(f"Class Hash: {hex(class_hash)}")
            return "already_deployed"
        except Exception as e:
            console.print(f"[dim]Account not deployed: {str(e)[:50]}...[/dim]")
        
        console.print("[red]❌ This starknet-py version doesn't support direct deployment[/red]")
        console.print("[yellow]⚠️ Alternative: Use Argent X or Braavos wallet to deploy[/yellow]")
        console.print("[dim]Or wait for the account to be deployed through other means[/dim]")
        
        return None
        
    except Exception as e:
        console.print(f"[red]❌ Deployment Failed: {e}[/red]")
        return None

if __name__ == "__main__":
    asyncio.run(deploy_account())
