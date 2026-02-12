import asyncio
import os
import sys
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping
from rich.console import Console

console = Console()

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()
    
    # Robust mapping logic
    if "STARKNET_PRIVATE_KEY" not in os.environ:
        if "PRIVATE_KEY" in os.environ:
            os.environ["STARKNET_PRIVATE_KEY"] = os.environ["PRIVATE_KEY"]
        elif "SOLANA_PRIVATE_KEY" in os.environ:
            import base58
            pk_bytes = base58.b58decode(os.environ["SOLANA_PRIVATE_KEY"])
            os.environ["STARKNET_PRIVATE_KEY"] = hex(int.from_bytes(pk_bytes[:32], 'big'))
            
    if "STARKNET_MAINNET_URL" not in os.environ:
        for alias in ["STARKNET_RPC_URL", "STARKNET_LAVA_URL", "STARKNET_1RPC_URL"]:
            if os.environ.get(alias):
                os.environ["STARKNET_MAINNET_URL"] = os.environ[alias]
                break

async def main():
    load_env()
    
    rpc_url = os.getenv("STARKNET_MAINNET_URL")
    pk_str = os.getenv("STARKNET_PRIVATE_KEY")
    addr_str = os.getenv("STARKNET_WALLET_ADDRESS")

    if not all([rpc_url, pk_str, addr_str]):
        console.print("[red]❌ Missing required environment variables (RPC_URL, PRIVATE_KEY, WALLET_ADDRESS).[/red]")
        return

    private_key = int(pk_str, 16)
    address = int(addr_str, 16)
    
    client = FullNodeClient(node_url=rpc_url)
    key_pair = KeyPair.from_private_key(private_key)

    console.print(f"🚀 [bold blue]Attempting Activation for:[/bold blue] {hex(address)}")

    # 2. Configure Deployment
    # These bounds are generous to ensure success on first try
    resource_bounds = ResourceBoundsMapping(
        l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
        l2_gas=ResourceBounds(max_amount=int(1e6), max_price_per_unit=int(1e17))
    )

    # 3. Trigger Deploy
    # Standard OpenZeppelin Hash provided by user
    OZ_CLASS_HASH = 0x0539f522860b093c83664d4c5709968853f3e828d57d740f941f1738722a4501
    
    try:
        deploy_result = await Account.deploy_account_v3(
            address=address,
            class_hash=OZ_CLASS_HASH,
            salt=0, 
            key_pair=key_pair,
            client=client,
            resource_bounds=resource_bounds,
            chain=StarknetChainId.MAINNET,
        )
        
        console.print(f"[bold green]✅ Activation Broadcast![/bold green] Hash: [cyan]{hex(deploy_result.hash)}[/cyan]")
        console.print("[dim]⌛ Waiting for L2 Acceptance...[/dim]")
        await deploy_result.wait_for_acceptance()
        console.print("[bold green]🎉 ACCOUNT ACTIVE. 'execute_v3' is now unlocked.[/bold green]")

    except Exception as e:
        console.print(f"[bold red]❌ Activation Failed:[/bold red] {e}")
        if "Contract already deployed" in str(e) or "is already used" in str(e):
            console.print("[yellow]💡 Suggestion: Account might already be active. Try running gas_refuel.py.[/yellow]")
        elif "address" in str(e).lower() and "match" in str(e).lower():
            console.print("[red]⚠️  Address Mismatch: The derived address from your Private Key does not match the wallet address in .env.[/red]")
            console.print("[red]Check if you are using the correct Private Key for that address.[/red]")

if __name__ == "__main__":
    asyncio.run(main())
