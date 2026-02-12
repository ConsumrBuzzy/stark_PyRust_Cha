"""
ADR-049: Ghost Sweep Recovery
=============================
Derives the Starknet 'Ghost Address' from EVM keys and sweeps funds.
"""

import os
import sys
import json
from rich.console import Console
from rich.panel import Panel

# Add python-logic to path
sys.path.append(os.path.join(os.getcwd(), 'python-logic'))

from strategy_module import RefiningStrategy

console = Console()

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

def get_ghost_address():
    evm_addr = os.getenv("TRANSIT_EVM_ADDRESS")
    if not evm_addr:
        return None
    
    # Strip 0x
    clean = evm_addr.lower().replace("0x", "")
    # Pad to 64 chars (32 bytes)
    ghost = "0x" + clean.zfill(64)
    return ghost

def find_funds():
    ghost = get_ghost_address()
    if not ghost:
        console.print("[red]❌ TRANSIT_EVM_ADDRESS not in .env[/red]")
        return

    console.print(Panel.fit(f"[bold cyan]🔍 Locating Ghost Funds[/bold cyan]\n"
                          f"EVM Base: {os.getenv('TRANSIT_EVM_ADDRESS')}\n"
                          f"Starknet Ghost: [green]{ghost}[/green]"))
    
    strategy = RefiningStrategy(dry_run=True)
    try:
        wei = strategy.starknet.get_eth_balance(ghost)
        eth = wei / 1e18
        console.print(f"💰 [bold]Ghost Balance:[/bold] [green]{eth:.6f} ETH[/green]")
        
        if eth > 0:
            console.print("[yellow]✨ Funds detected! You can now run --sweep[/yellow]")
        else:
            console.print("[dim]No funds detected yet. Bridge may be pending...[/dim]")
            
    except Exception as e:
        console.print(f"[red]Error checking ghost balance: {e}[/red]")

def sweep_funds():
    ghost = get_ghost_address()
    target = os.getenv("STARKNET_WALLET_ADDRESS")
    priv_key = os.getenv("TRANSIT_EVM_PRIVATE_KEY")
    
    if not ghost or not target or not priv_key:
        console.print("[red]❌ Missing required env variables (TRANSIT_EVM_ADDRESS, STARKNET_WALLET_ADDRESS, TRANSIT_EVM_PRIVATE_KEY)[/red]")
        return

    console.print(Panel.fit(f"[bold red]🧹 INITIATING GHOST SWEEP[/bold red]\n"
                          f"From: {ghost}\n"
                          f"To: {target}"))
    
    console.print("[yellow]⚠️  Note: This requires the Ghost Address to be an EOA-compatible account on Starknet.[/yellow]")
    console.print("[dim]Simulating transfer... (Real sweep logic matches orchestrator logic)[/dim]")
    
    # In a real scenario, we'd use the EVM private key to sign a Starknet transaction.
    # For now, we report the plan and check if user wants to proceed with actual signing.
    
    strategy = RefiningStrategy(dry_run=True)
    # Placeholder for actual sweep execution
    console.print("[cyan]Sweep Logic:[/cyan] Sending [bold]ALL[/bold] ETH from Ghost -> Game Wallet.")
    
    # We will implement the actual Secp256k1 signing once funds are confirmed.

if __name__ == "__main__":
    load_env()
    if "--find" in sys.argv:
        find_funds()
    elif "--sweep" in sys.argv:
        sweep_funds()
    else:
        console.print("Usage: python rescue_funds.py [--find | --sweep]")
        # Auto-run find to be helpful
        find_funds()
