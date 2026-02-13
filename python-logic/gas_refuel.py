import os
import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from foundation.legacy_env import load_env_manual
    from foundation.security import SecurityManager
    from foundation.network import NetworkOracle
    from engines.gas_refuel import GasRefuelEngine
except Exception as e:
    print(f"❌ Failed to import core modules: {e}")
    raise

console = Console()


def build_engine() -> GasRefuelEngine:
    load_env_manual()
    network_oracle = NetworkOracle()
    security_manager = SecurityManager()
    return GasRefuelEngine(network_oracle, security_manager)


async def main():
    engine = build_engine()
    quote = engine.get_swap_quote()
    if not quote:
        return

    confirm = "--confirm" in sys.argv
    result = await engine.execute_swap(quote, confirm=confirm)

    if not result.get("success"):
        console.print(f"[red]❌ {result.get('error')}")
        return

    if result.get("dry_run"):
        console.print("[yellow]⚠ Simulation only. Re-run with --confirm to execute.[/yellow]")
        return

    console.print(f"[bold green]✨ Swap Broadcasted![/bold green]")
    console.print(f"Transaction Hash: [cyan]{result.get('tx_hash')}[/cyan]")
    console.print("[dim]Waiting for inclusion...[/dim]")


if __name__ == "__main__":
    asyncio.run(main())
