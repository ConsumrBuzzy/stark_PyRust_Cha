import os
import sys
from web3 import Web3
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

def check_base():
    load_env()
    addr = os.getenv("TRANSIT_EVM_ADDRESS")
    if not addr:
        console.print("[red]❌ TRANSIT_EVM_ADDRESS not found in .env[/red]")
        return

    # Use public Base RPC
    w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
    
    try:
        if not w3.is_connected():
            console.print("[red]❌ Could not connect to Base Network.[/red]")
            return

        balance_wei = w3.eth.get_balance(addr)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        
        console.print(f"--- Base Network Check ---")
        console.print(f"Address: {addr}")
        console.print(f"Balance: [bold green]{balance_eth:.8f} ETH[/bold green]")
        
        if balance_eth > 0.001:
            console.print("\n[yellow]💡 Funds are safe on Base. The bridge failed to broadcast.[/yellow]")
        else:
            console.print("\n[red]❓ Balance is empty. Potential double-spend or confirmed bridge elsewhere.[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")

if __name__ == "__main__":
    check_base()
