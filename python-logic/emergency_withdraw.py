"""
Emergency Withdraw - Atomic Deploy + Transfer for StarkNet v0.14.0+
====================================================================
Burn-and-Exit protocol for extracting funds from undeployed accounts.
"""

import os
import sys
import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# Add src to path for shared env/engine
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from foundation.legacy_env import load_env_manual
    from foundation.network import NetworkOracle
    from foundation.security import SecurityManager
    from engines.emergency import EmergencyWithdrawEngine
except Exception as e:
    print(f"❌ Failed to import core modules: {e}")
    sys.exit(1)

console = Console()

def ensure_env():
    load_env_manual()


async def execute_emergency_withdraw(target_address: str, confirm: bool) -> bool:
    ensure_env()

    network_oracle = NetworkOracle()
    security_manager = SecurityManager()
    engine = EmergencyWithdrawEngine(network_oracle, security_manager)

    result = await engine.execute(target_address=target_address, confirm=confirm)

    console.print(Panel.fit(
        f"[bold red]🚨 EMERGENCY WITHDRAW[/bold red]\n"
        f"Target: {target_address}\n"
        f"Mode: Atomic Deploy + Transfer",
        title="Burn-and-Exit Protocol"
    ))

    if not result.success:
        console.print(f"[bold red]❌ {result.message}[/bold red]")
        return False

    console.print(f"[cyan]Balance: {result.balance_eth:.6f} ETH | Deployed: {result.deployed}[/cyan]")

    if result.dry_run:
        console.print("[yellow]⚠ Simulation only. Re-run with --confirm to execute.[/yellow]")
        console.print(f"Planned amount: {result.amount_eth:.6f} ETH")
        return True

    console.print(f"[bold green]✨ WITHDRAWAL BROADCASTED![/bold green]")
    console.print(f"Transaction Hash: [cyan]{result.tx_hash}[/cyan]")
    console.print(f"Amount: {result.amount_eth:.6f} ETH")
    console.print(f"Target: {result.target_address}")
    return True


if __name__ == "__main__":
    target_address = "0xfF01E0776369Ce51debb16DFb70F23c16d875463"  # Transit wallet
    confirm = "--confirm" in sys.argv

    console.print(Panel.fit(
        f"[bold cyan]🎯 Extraction Target[/bold cyan]\n"
        f"Withdrawing to: {target_address}\n"
        f"[dim]Using transit wallet as safe destination[/dim]",
        title="Emergency Withdraw"
    ))

    asyncio.run(execute_emergency_withdraw(target_address, confirm=confirm))
