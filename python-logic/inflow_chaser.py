"""
ADR-060: Inflow Chaser (CDP SDK)
================================
Automates gasless USDC transfer from Coinbase to Phantom (Base)
using the Coinbase Developer Platform (CDP) SDK.
"""

import os
import sys
from cdp import Wallet, Coinbase, Cdp
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
        
    # Standard CDP configuration
    try:
        Cdp.configure(api_key_name, api_key_private.replace("\\n", "\n"))
        return True
    except Exception as e:
        console.print(f"[red]❌ CDP Configuration Error: {e}[/red]")
        return False

def send_chaser_usdc(amount=15.00):
    if not setup_cdp(): return
    
    # Use your existing Phantom EVM Address from .env
    phantom_addr = os.getenv("TRANSIT_EVM_ADDRESS")
    if not phantom_addr:
        console.print("[red]❌ TRANSIT_EVM_ADDRESS not found in .env[/red]")
        return

    console.print(f"[blue]🚀 Initiating $15 USDC Gasless Transfer to {phantom_addr}...[/blue]")
    
    try:
        # Create/Load a temporary or persisted CDP wallet
        # For simplicity, we create a new one, but for industrial use, we'd load a fixed wallet.
        wallet = Wallet.create(network_id="base-mainnet")
        
        # Note: This assumes the CDP wallet has balance. 
        # If withdrawing from Coinbase 'Main' account to Phantom:
        transfer = wallet.transfer(
            amount, 
            Coinbase.assets.usdc, 
            phantom_addr, 
            gasless=True
        ).wait()
        
        console.print(f"[bold green]✅ $15 USDC landed on Phantom (Base).[/bold green]")
        console.print(f"Hash: {transfer.transaction_hash}")
        
    except Exception as e:
        console.print(f"[bold red]❌ CDP Transfer Failed: {e}[/bold red]")

if __name__ == "__main__":
    send_chaser_usdc()
