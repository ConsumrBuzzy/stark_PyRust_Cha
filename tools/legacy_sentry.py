"""
Ghost Sentry Loop - Automated $15 Recovery
========================================
Monitors Ghost address and auto-sweeps funds to Coinbase
"""

import os
import sys
import time
import asyncio
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

# Add repo root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ops.ghost_monitor import load_settings, check_ghost_balance, sweep_recommended
# Fallback to existing sweep function if present
try:
    from rescue_funds import sweep_funds  # type: ignore
except Exception:  # pragma: no cover
    sweep_funds = None

console = Console()

async def ghost_sentry_loop():
    """Main sentry loop for Ghost address monitoring"""

    settings = load_settings()
    console.print(Panel.fit(
        "[bold red]🚨 GHOST SENTRY LOOP ACTIVATED[/bold red]\n"
        "Main Wallet Decommissioned\n"
        "Monitoring: $15 Bridge Funds\n"
        "Target: Coinbase Starknet",
        title="Clean Break Protocol"
    ))

    ghost_addr = settings.ghost_address
    if not ghost_addr:
        console.print("[red]❌ Cannot get Ghost address[/red]")
        return

    console.print(f"👻 Monitoring: {ghost_addr}")

    # Coinbase Starknet address (fallback to transit if not set)
    coinbase_addr = os.getenv("COINBASE_STARKNET_ADDRESS") or settings.main_address

    poll_interval = 300  # 5 minutes
    threshold = float(settings.ghost_threshold_eth)

    console.print(f"⏰ Poll Interval: {poll_interval}s")
    console.print(f"💰 Threshold: {threshold} ETH")
    console.print(f"🎯 Target: {coinbase_addr}")
    
    poll_count = 0
    max_polls = 288  # 24 hours at 5-minute intervals
    
    while poll_count < max_polls:
        poll_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        console.print(f"\n[dim]{timestamp} - Poll {poll_count}/{max_polls}[/dim]")
        
        try:
            balance, rpc_used = await check_ghost_balance(use_rpc_rotation=True, settings=settings)
            
            if balance > threshold:
                console.print(f"[bold green]💰 FUNDS DETECTED: {balance:.6f} ETH[/bold green]")
                console.print(f"[bold yellow]🚀 INITIATING AUTO-SWEEP...[/bold yellow]")
                
                if sweep_funds and sweep_recommended(balance, settings):
                    sweep_result = sweep_funds()
                    if sweep_result:
                        console.print(Panel.fit(
                            f"[bold green]✅ RECOVERY COMPLETE[/bold green]\n"
                            f"Amount: {balance:.6f} ETH\n"
                            f"Value: ${balance * 2200:.2f} USD\n"
                            f"Target: {coinbase_addr}",
                            title="Mission Success"
                        ))
                        with open("recovery_log.txt", "a") as f:
                            f.write(f"{timestamp} - RECOVERED: {balance:.6f} ETH to {coinbase_addr}\n")
                        console.print("[dim]🏁 Ghost Sentry Loop terminated[/dim]")
                        return
                    else:
                        console.print("[red]❌ Sweep failed, continuing monitoring[/red]")
                else:
                    console.print("[yellow]⚠️ Sweep function unavailable or not recommended; continuing monitoring[/yellow]")
            else:
                console.print(f"[dim]💰 Ghost Balance: {balance:.6f} ETH[/dim]")
                console.print("[dim]No funds detected. Continuing sentry...[/dim]")
                
        except Exception as e:
            console.print(f"[red]❌ Poll error: {e}[/red]")
        
        # Wait for next poll
        if poll_count < max_polls:
            console.print(f"[dim]⏳ Waiting {poll_interval}s...[/dim]")
            time.sleep(poll_interval)
    
    # Max polls reached
    console.print(Panel.fit(
        "[bold yellow]⏰ TIME LIMIT REACHED[/bold yellow]\n"
        "24 hours elapsed without detection\n"
        "Manual intervention required",
        title="Sentry Timeout"
    ))

if __name__ == "__main__":
    asyncio.run(ghost_sentry_loop())
