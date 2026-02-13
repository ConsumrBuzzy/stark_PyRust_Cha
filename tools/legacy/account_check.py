import asyncio
import os
from starknet_py.net.full_node_client import FullNodeClient
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

async def check_deployment():
    load_env()
    rpc_url = os.getenv("STARKNET_MAINNET_URL")
    wallet_addr = os.getenv("STARKNET_WALLET_ADDRESS")
    
    if not rpc_url or not wallet_addr:
        console.print("[red]❌ Missing RPC or Wallet in .env[/red]")
        return

    client = FullNodeClient(node_url=rpc_url)
    
    try:
        class_hash = await client.get_class_hash_at(int(wallet_addr, 16))
        console.print(f"✅ Account [bold green]IS DEPLOYED[/bold green]. Class Hash: {hex(class_hash)}")
    except Exception as e:
        if "Contract not found" in str(e):
            console.print(f"⌛ Account [bold yellow]NOT DEPLOYED[/bold yellow] (Not Activated).")
            console.print("[dim]Note: You can have a balance without being deployed, but you cannot spend funds until activated.[/dim]")
        else:
            console.print(f"[red]❌ Error: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(check_deployment())
