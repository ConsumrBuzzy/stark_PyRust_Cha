import os
import sys
import asyncio
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call
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

async def check_strk_balance():
    load_env()
    wallet = os.getenv("STARKNET_WALLET_ADDRESS")
    rpc_url = os.getenv("STARKNET_MAINNET_URL") or os.getenv("STARKNET_RPC_URL")
    
    if not wallet or not rpc_url:
        console.print("[red]❌ Missing Wallet or RPC URL in .env[/red]")
        return

    strk_address = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"
    client = FullNodeClient(node_url=rpc_url)
    
    try:
        call = Call(
            to_addr=int(strk_address, 16),
            selector=get_selector_from_name("balanceOf"),
            calldata=[int(wallet, 16)]
        )
        res = await client.call_contract(call)
        balance_wei = res[0]
        balance_strk = balance_wei / 10**18
        
        console.print(f"--- Starknet STRK Check ---")
        console.print(f"Wallet: {wallet}")
        console.print(f"Balance: [bold green]{balance_strk:.6f} STRK[/bold green]")
        
        if balance_strk < 0.1:
            console.print("\n[yellow]⚠ Warning: STRK balance is low. This may cause 'Insufficient Funds' errors for game actions.[/yellow]")
        else:
            console.print("\n[green]✅ STRK balance looks healthy.[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ Error fetching balance: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(check_strk_balance())
