import asyncio
import os
import sys
from pathlib import Path
from rich.console import Console

# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from foundation.legacy_env import load_env_manual
    from foundation.security import SecurityManager
    from foundation.network import NetworkOracle
    from engines.rescue import RescueEngine
except Exception as e:
    print(f"❌ Failed to import core modules: {e}")
    raise

console = Console()


async def rescue(target_address_hex, destination_address_hex, amount_wei=None):
    load_env_manual()
    network_oracle = NetworkOracle()
    security_manager = SecurityManager()
    engine = RescueEngine(network_oracle, security_manager)

    result = await engine.force_transfer(
        from_address=target_address_hex,
        destination=destination_address_hex,
        amount_wei=amount_wei,
    )

    if result.get("success"):
        console.print(f"✅ [bold green]EXTRACTED![/bold green] Hash: [cyan]{result.get('tx_hash')}[/cyan]")
        console.print(f"   From: {result.get('from')}\n   To: {result.get('to')}\n   Amount: {result.get('amount_wei') / 1e18:.6f} ETH")
    else:
        console.print(f"[bold red]❌ Extraction Failed:[/bold red] {result.get('error')}")


if __name__ == "__main__":
    GHOST_ADDR = os.getenv("STARKNET_GHOST_ADDRESS") or "0xGHOST"
    MAIN_ADDR = os.getenv("STARKNET_WALLET_ADDRESS") or "0xMAIN"
    DEST = os.getenv("RESCUE_DESTINATION") or "0xUSER_COINBASE_OR_PHANTOM_ADDRESS"

    target = GHOST_ADDR
    if len(sys.argv) > 1 and sys.argv[1] == "--main":
        target = MAIN_ADDR

    asyncio.run(rescue(target, DEST))
