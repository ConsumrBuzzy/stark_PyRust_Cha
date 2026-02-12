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
    wallet_addr = "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
    priv_key = "0x06d44f5b497e5222d3c6fe5158d3b73a575450575b99d2101c5c180d07bc318b"
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
        console.print("[yellow]🔧 Deploying account...[/yellow]")
        
        # Create account for deployment
        account = Account(
            address=wallet_addr,
            client=client,
            key_pair=key_pair,
            chain=StarknetChainId.MAINNET
        )
        
        # Deploy the account
        deploy_result = await account.sign_deploy_account_v1(
            class_hash=account_class_hash,
            contract_address_salt=0x1234,
            max_fee=int(0.01 * 10**18)  # 0.01 ETH max fee
        )
        
        console.print(f"[green]✅ Deployment transaction created![/green]")
        console.print(f"Transaction Hash: [cyan]{hex(deploy_result.transaction_hash)}[/cyan]")
        
        # Broadcast transaction
        invoke_tx = await client.deploy_account(deploy_result)
        console.print(f"[bold green]🚀 DEPLOYMENT BROADCASTED![/bold green]")
        console.print(f"View on Starkscan: https://starkscan.co/tx/{hex(invoke_tx.transaction_hash)}")
        
        # Wait for confirmation
        console.print("[dim]Waiting for deployment confirmation...[/dim]")
        await client.wait_for_tx(invoke_tx.transaction_hash)
        console.print("[bold green]✅ ACCOUNT DEPLOYED SUCCESSFULLY![/bold green]")
        
        return invoke_tx.transaction_hash
        
    except Exception as e:
        console.print(f"[red]❌ Deployment Failed: {e}[/red]")
        return None

if __name__ == "__main__":
    asyncio.run(deploy_account())
