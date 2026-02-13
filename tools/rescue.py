"""
ADR-049: Ghost Sweep Recovery
=============================
Derives the Starknet 'Ghost Address' from EVM keys and sweeps funds.
"""

import os
import sys
import json
import time
from rich.console import Console
from rich.panel import Panel

# Add repo root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ops.ghost_monitor import load_settings, balance_with_rotation, sweep_recommended

console = Console()

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

# ADR-047: Load environment IMMEDIATELY to populate global objects
load_env()
settings = load_settings()

def get_ghost_address():
    return settings.ghost_address

import asyncio


async def check_starknet_balance(address: str):
    bal, rpc_used = await balance_with_rotation(address, settings.rpc_urls, settings.eth_contract)
    return float(bal) if bal is not None else 0.0

def find_funds():
    verbose = "--verbose" in sys.argv or "--direct-query" in sys.argv
    poll_mode = "--poll" in sys.argv
    ghost = get_ghost_address()
    if not ghost:
        console.print("[red]❌ TRANSIT_EVM_ADDRESS not in .env[/red]")
        return

    rpc_url = os.getenv("STARKNET_MAINNET_URL") or os.getenv("STARKNET_RPC_URL")
    if verbose:
        console.print(f"[dim]Debug: Using Ghost Address {ghost}[/dim]")
        console.print(f"[dim]Debug: RPC URL: {rpc_url}[/dim]")

    console.print(Panel.fit(f"[bold cyan]🔍 Locating Ghost Funds[/bold cyan]\n"
                          f"EVM Base: {os.getenv('TRANSIT_EVM_ADDRESS')}\n"
                          f"Starknet Ghost: [green]{ghost}[/green]"))
    
    # Polling Loop
    max_tries = 100 if poll_mode else 1
    interval = 120 if poll_mode else 0
    
    for i in range(max_tries):
        if i > 0:
            console.print(f"[dim]{time.strftime('%H:%M:%S')} - Poll {i+1}/{max_tries}: Waiting {interval}s...[/dim]")
            time.sleep(interval)
            
        eth = asyncio.run(check_starknet_balance(ghost))
        
        if eth > 0:
            console.print(f"💰 [bold green]GHOST BALANCE DETECTED: {eth:.8f} ETH[/bold green]")
            console.print("[bold yellow]🚀 TRIGGERING AUTO-SWEEP...[/bold yellow]")
            sweep_funds()
            return
        elif not poll_mode:
            console.print(f"💰 [bold white]Ghost Balance: {eth:.6f} ETH[/bold white]")
            console.print("[dim]No funds detected yet.[/dim]")

    if poll_mode:
        console.print("[yellow]Polling cycle finished or timed out.[/yellow]")

def sweep_funds():
    ghost = get_ghost_address()
    target = settings.main_address
    priv_key = os.getenv("TRANSIT_EVM_PRIVATE_KEY")
    
    if not ghost or not target or not priv_key:
        console.print("[red]❌ Missing required env variables[/red]")
        return

    console.print(Panel.fit(f"[bold red]🧹 INITIATING GHOST SWEEP[/bold red]\n"
                          f"From: {ghost}\n"
                          f"To: {target}"))
    
    # Check latest balance before sweep
    bal, _ = asyncio.run(balance_with_rotation(ghost, settings.rpc_urls, settings.eth_contract))
    if bal is None or bal <= settings.ghost_threshold_eth:
        console.print(f"[yellow]⚠️ Balance {bal or 0:.6f} ETH below threshold; sweep skipped[/yellow]")
        return

    # Placeholder: actual sweep signing not implemented
    if "--confirm" in sys.argv:
        console.print("[bold red]☢️ BROADCASTING (stub) SECP256K1 TRANSACTION...[/bold red]")
    else:
        console.print("[yellow]Simulation only. Run with --confirm to sign and broadcast (not implemented).[/yellow]")

if __name__ == "__main__":
    load_env()
    if "--find" in sys.argv:
        find_funds()
    elif "--sweep" in sys.argv:
        sweep_funds()
    else:
        find_funds()
