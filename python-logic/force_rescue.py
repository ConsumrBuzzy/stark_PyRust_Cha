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
    
    if "STARKNET_MAINNET_URL" not in os.environ:
        for alias in ["STARKNET_RPC_URL", "STARKNET_LAVA_URL", "STARKNET_1RPC_URL"]:
            if os.environ.get(alias):
                os.environ["STARKNET_MAINNET_URL"] = os.environ[alias]
                break

async def rescue(target_address_hex, destination_address_hex, amount_wei=None):
    load_env()
    rpc_url = os.getenv("STARKNET_MAINNET_URL")
    pk_str = os.getenv("STARKNET_PRIVATE_KEY")
    
    if not all([rpc_url, pk_str]):
        console.print("[red]❌ Missing RPC or Private Key in .env[/red]")
        return

    client = FullNodeClient(node_url=rpc_url)
    key_pair = KeyPair.from_private_key(int(pk_str, 16))
    
    account = Account(
        address=int(target_address_hex, 16),
        client=client,
        key_pair=key_pair,
        chain=StarknetChainId.MAINNET,
    )

    console.print(f"📡 [bold blue]Scanning Address:[/bold blue] {target_address_hex}")
    
    try:
        balance = await account.get_balance()
        console.print(f"💰 [bold green]Balance Found:[/bold green] {balance / 1e18:.6f} ETH")
        
        if balance == 0:
            console.print("[yellow]⌛ Balance is zero. Extraction suspended until funds arrive.[/yellow]")
            return

        if amount_wei is None:
            # Leave room for gas (approx 0.0005 ETH)
            amount_wei = int(balance - 500000000000000) 
            if amount_wei <= 0:
                console.print("[red]❌ Balance too low to cover gas fees.[/red]")
                return

        console.print(f"🚀 [bold cyan]Forcing Extraction...[/bold cyan]")
        console.print(f"   Dest: {destination_address_hex}")
        console.print(f"   Amt:  {amount_wei / 1e18:.6f} ETH")

        # Prepare transfer
        transfer_call = account.prepare_transfer_call(
            to_addr=int(destination_address_hex, 16),
            amount=amount_wei
        )

        # Standard Resource Bounds for v0.14.0 compatibility
        resource_bounds = ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l2_gas=ResourceBounds(max_amount=int(1e6), max_price_per_unit=int(1e17)),
            l1_data_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13))
        )

        # Broadcast
        # Note: If undeployed, this will fail unless we add deployment logic.
        # But this script is for "Forcing" the interaction assuming the signer is valid.
        response = await account.execute_v3(
            calls=[transfer_call],
            resource_bounds=resource_bounds
        )
        
        console.print(f"✅ [bold green]EXTRACTED![/bold green] Hash: [cyan]{hex(response.hash)}[/cyan]")
        await response.wait_for_acceptance()
        console.print("🎉 [bold green]Extraction confirmed on L2.[/bold green]")

    except Exception as e:
        console.print(f"[bold red]❌ Extraction Failed:[/bold red] {e}")
        if "Contract not found" in str(e):
             console.print("[yellow]💡 Account is NOT DEPLOYED. You must activate it in the UI first (ADR-067).[/yellow]")

if __name__ == "__main__":
    # USER: Update these two addresses as needed
    GHOST_ADDR = "0x000000000000000000000000ff01e0776369ce51debb16dfb70f23c16d875463"
    MAIN_ADDR = "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
    
    # Destination (Phantom Base Transit or Coinbase)
    # Defaulting to a placeholder for user to fill
    DEST = "0xUSER_COINBASE_OR_PHANTOM_ADDRESS" 
    
    import sys
    target = GHOST_ADDR
    if len(sys.argv) > 1 and sys.argv[1] == "--main":
        target = MAIN_ADDR
        
    asyncio.run(rescue(target, DEST))
