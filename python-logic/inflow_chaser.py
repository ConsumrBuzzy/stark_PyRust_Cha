import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from foundation.legacy_env import load_env_manual
    from engines.cdp_chaser import CdpChaserEngine
except Exception as e:
    print(f"❌ Failed to import core modules: {e}")
    raise

console = Console()


def build_engine() -> CdpChaserEngine:
    load_env_manual()
    api_key_name = os.getenv("COINBASE_CLIENT_API_KEY", "")
    api_key_private = os.getenv("COINBASE_API_PRIVATE_KEY", "")
    transit_address = os.getenv("TRANSIT_EVM_ADDRESS", "")
    return CdpChaserEngine(api_key_name, api_key_private, transit_address)


def send_chaser_usdc(amount: float = 15.00):
    engine = build_engine()
    console.print(Panel.fit(f"🚀 Initiating $[bold]{amount}[/bold] USDC Gasless Transfer", title="CDP Inflow Chaser"))
    tx_hash = engine.send_usdc(amount=amount)
    if tx_hash:
        console.print(f"[green]✅ USDC landed. Hash: {tx_hash}[/green]")


if __name__ == "__main__":
    send_chaser_usdc()
