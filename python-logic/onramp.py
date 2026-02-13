"""
Coinbase Onramp Driver (PhantomArbiter Port)
============================================
Adapted for stark_PyRust_Chain.
Uses CCXT + CDP Authentication to bridge funds to Starknet.
"""

import os
import time
import asyncio
import sys
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from foundation.legacy_env import load_env_manual
    from engines.onramp import CoinbaseOnrampEngine
except Exception as e:
    print(f"❌ Failed to import core modules: {e}")
    raise

console = Console()


def build_engine(dry_run: bool) -> Optional[CoinbaseOnrampEngine]:
    load_env_manual()
    transit_address = os.getenv("TRANSIT_EVM_ADDRESS", "")
    api_key_name = os.getenv("COINBASE_CLIENT_API_KEY", "")
    api_private_key = os.getenv("COINBASE_API_PRIVATE_KEY", "")
    return CoinbaseOnrampEngine(transit_address, api_key_name, api_private_key, dry_run=dry_run)


async def main():
    is_dry = "--no-dry-run" not in sys.argv
    engine = build_engine(dry_run=is_dry)
    if not engine:
        return

    console.print(Panel.fit("[bold blue]🌉 Coinbase -> Base (Transit)[/bold blue]"))

    result = await engine.bridge_funds()

    if not result.success:
        console.print(f"[red]❌ {result.message}[/red]")
        if result.amount_eth is not None:
            console.print(f"Balance: {result.amount_eth:.4f} ETH")
        return

    if result.dry_run:
        console.print(Panel(f"Simulating Withdrawal:\nAsset: ETH\nAmount: {result.amount_eth:.4f}\nNetwork: base\nTarget: {engine.transit_address}", title="[DRY RUN]"))
    else:
        console.print(f"[green]✅ Withdrawal to Base Initialized! ID: {result.withdrawal_id}")
        console.print("[dim]Next Step: Run 'python python-logic/bridge_logic.py' once funds arrive.[/dim]")

    await engine.close()


if __name__ == "__main__":
    asyncio.run(main())
