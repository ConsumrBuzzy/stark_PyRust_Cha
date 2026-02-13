"""
ADR-058: Chaser Strategy (Headless Bridge)
Signs and sends a small "chaser" from transit wallet to StarkNet via Orbiter.
Now delegates to core OrbiterBridgeAdapter.
"""

import os
import sys
import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from web3 import Web3

# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from foundation.legacy_env import load_env_manual
    from foundation.security import SecurityManager
    from foundation.constants import BASE_RPC_URL
    from engines.bridge_system import OrbiterBridgeAdapter
except Exception as e:
    print(f"❌ Failed to import core modules: {e}")
    raise

console = Console()


async def send_chaser(amount_eth: float = 0.0063, dry_run: bool = True):
    load_env_manual()

    # Base RPC + security manager
    w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
    security_manager = SecurityManager()
    await security_manager.initialize()

    adapter = OrbiterBridgeAdapter(
        base_web3=w3,
        security_manager=security_manager,
        maker_address="0xe530d28960d48708ccf3e62aa7b42a80bc427aef",
        destination_code=9004,
        min_amount_eth=0.005,
    )

    priv_key = os.getenv("TRANSIT_EVM_PRIVATE_KEY")
    if not priv_key:
        console.print("[red]❌ TRANSIT_EVM_PRIVATE_KEY missing.[/red]")
        return

    try:
        account = w3.eth.account.from_key(priv_key)
    except Exception as e:
        console.print(f"[red]❌ Invalid EVM key: {e}[/red]")
        return

    console.print(Panel(f"🚀 [bold]Initiating ADR-058 Chaser[/bold]\nDest: Starknet\nAmt: {amount_eth} ETH", title="Chaser Engine"))

    balance = await adapter.get_balance(account.address)
    if balance < amount_eth:
        console.print(f"[red]⛔ Insufficient balance: {balance:.6f} ETH < {amount_eth} ETH[/red]")
        return

    result = await adapter.bridge_to_starknet(
        amount_eth=amount_eth,
        transit_address=account.address,
        dry_run=dry_run,
        override_key=priv_key,
    )

    if result.get("dry_run"):
        payload = result.get("payload", {})
        console.print(f"[yellow][DRY RUN][/yellow] Tx Payload: {payload}")
        return

    if result.get("success"):
        console.print(f"[bold green]✅ Chaser Sent![/bold green] Hash: {result.get('tx_hash')}")
    else:
        console.print(f"[bold red]❌ Chaser failed: {result.get('error')}[/bold red]")


if __name__ == "__main__":
    is_dry = "--no-dry-run" not in sys.argv
    asyncio.run(send_chaser(dry_run=is_dry))
