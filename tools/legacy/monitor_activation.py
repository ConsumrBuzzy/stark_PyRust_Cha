import asyncio
import os
import time
from starknet_py.net.full_node_client import FullNodeClient
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table

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

async def check_status(client, wallet_addr, ghost_addr):
    status = {"account": "PENDING", "ghost_bal": "0.0"}
    
    # 1. Check Deployment
    try:
        await client.get_class_hash_at(int(wallet_addr, 16))
        status["account"] = "✅ ACTIVE"
    except:
        status["account"] = "⌛ UNDEPLOYED"

    # 2. Check Ghost Balance
    try:
        # Using eth_get_balance for the ghost address (it's technically a contract address at index 0)
        bal = await client.get_balance(int(ghost_addr, 16))
        status["ghost_bal"] = f"{bal / 1e18:.6f} ETH"
    except:
        status["ghost_bal"] = "0.000000 ETH"
        
    return status

async def main():
    load_env()
    rpc_url = os.getenv("STARKNET_MAINNET_URL")
    wallet_addr = os.getenv("STARKNET_WALLET_ADDRESS")
    evm_addr = os.getenv("TRANSIT_EVM_ADDRESS")
    
    # Derive Ghost Address (simplified logic from rescue_funds.py)
    clean = evm_addr.lower().replace("0x", "")
    ghost_addr = "0x" + clean.zfill(64)

    client = FullNodeClient(node_url=rpc_url)
    
    console.print(Panel(f"🔍 [bold blue]Monitoring Activation: {wallet_addr}[/bold blue]\n👻 [bold cyan]Ghost Address: {ghost_addr}[/bold cyan]", title="ADR-071: Recovery Monitor"))

    with Live(auto_refresh=False) as live:
        while True:
            stats = await check_status(client, wallet_addr, ghost_addr)
            
            table = Table(title=f"Last Pulse: {time.strftime('%H:%M:%S')}")
            table.add_column("Monitor Target", style="magenta")
            table.add_column("Status", style="cyan")
            
            table.add_row("Game Wallet (0x0517...)", stats["account"])
            table.add_row("Ghost Address (0xfF01...)", stats["ghost_bal"])
            
            live.update(table, refresh=True)
            
            if "ACTIVE" in stats["account"]:
                console.print("\n[bold green]🎉 ALERT: ACCOUNT ACTIVATION DETECTED![/bold green]")
                console.print("[green]Ready to execute gas_refuel.py and sweep_funds.py.[/green]")
                break
                
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
