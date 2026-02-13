"""
Argent Emergency Exit - Final Stand Protocol
Deploys Argent Web Wallet to unlock trapped funds (uses core DeploymentEngine).
"""

import os
import asyncio
from pathlib import Path
from rich.console import Console

# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from foundation.legacy_env import load_env_manual
    from foundation.security import SecurityManager
    from foundation.network import NetworkOracle
    from engines.deployment import DeploymentEngine
except Exception as e:
    print(f"❌ Failed to import core modules: {e}")
    raise

console = Console()


async def exit_protocol():
    load_env_manual()

    network_oracle = NetworkOracle()
    security_manager = SecurityManager()
    engine = DeploymentEngine(network_oracle, security_manager)

    argent_class_hash = int(os.getenv("ARGENT_CLASS_HASH", "0x01a7366993b74e484c2fa434313f89832207b53f609e25d26a27a26a27a26a27"), 16)

    console.print("🚀 EMERGENCY EXIT PROTOCOL")

    result = await engine.deploy_account_v3(
        class_hash=argent_class_hash,
        salt=0,
        constructor_calldata=None,
    )

    if not result.get("success"):
        console.print(f"❌ Salt 0 failed: {result.get('error')}")
        console.print("🔄 Trying salt=1...")
        result = await engine.deploy_account_v3(
            class_hash=argent_class_hash,
            salt=1,
            constructor_calldata=None,
        )

    if result.get("success"):
        console.print(f"✅ EXFILTRATION STARTED: {result['tx_hash']}")
        console.print(f"Deployed Address: {result.get('deployed_address')}")
    else:
        console.print("💀 Both deployment attempts failed.")
        console.print("🌐 Alternative: Visit portfolio.argent.xyz for manual recovery")


if __name__ == "__main__":
    asyncio.run(exit_protocol())
