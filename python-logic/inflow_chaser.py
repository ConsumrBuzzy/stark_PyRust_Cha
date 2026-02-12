import os
import sys
from cdp import Wallet, Cdp
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

def setup_cdp():
    load_env()
    api_key_name = os.getenv("COINBASE_CLIENT_API_KEY")
    api_key_private = os.getenv("COINBASE_API_PRIVATE_KEY")
    
    if not api_key_name or not api_key_private:
        console.print("[red]❌ CDP API credentials missing in .env[/red]")
        return False
        
    try:
        # Standard CDP configuration for v0.21.0+
        Cdp.configure(api_key_name, api_key_private.replace("\\n", "\n"))
        return True
    except Exception as e:
        console.print(f"[red]❌ CDP Configuration Error: {e}[/red]")
        return False

def send_chaser_usdc(amount=15.00):
    if not setup_cdp(): return
    
    phantom_addr = os.getenv("TRANSIT_EVM_ADDRESS")
    if not phantom_addr:
        console.print("[red]❌ TRANSIT_EVM_ADDRESS not found in .env[/red]")
        return

    console.print(f"[blue]🚀 Initiating $[bold]{amount}[/bold] USDC Gasless Transfer to {phantom_addr}...[/blue]")
    
    try:
        # Reuse existing wallet if available to bypass CreateWallet rate limits
        wallets = list(Wallet.list())
        wallet = next((w for w in wallets if w.network_id == "base-mainnet"), None)
        
        if not wallet:
            console.print("[yellow]⚠ No existing Base Mainnet wallet found. Attempting to create one...[/yellow]")
            wallet = Wallet.create(network_id="base-mainnet")
        else:
            console.print(f"[green]✅ Reusing existing CDP Wallet: {wallet.id}[/green]")
        
        # In v0.21.0, transfer takes (amount, asset_id, destination, gasless)
        transfer = wallet.transfer(
            amount, 
            "usdc", 
            phantom_addr, 
            gasless=True
        ).wait()
        
        console.print(f"[bold green]✅ USDC landed on Phantom (Base).[/bold green]")
        console.print(f"Hash: {transfer.transaction_hash}")
        
    except Exception as e:
        console.print(f"[bold red]❌ CDP Transfer Failed: {e}[/bold red]")

if __name__ == "__main__":
    send_chaser_usdc()
