"""
Final Rescue Attempt - Proxy Hash Deployment
Uses the discovered Argent Proxy class hash to unlock funds via core engines.
"""

import os
import asyncio
from pathlib import Path

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


async def main():
    """Final deployment attempt with discovered proxy hash"""
    load_env_manual()

    network_oracle = NetworkOracle()
    security_manager = SecurityManager()
    engine = DeploymentEngine(network_oracle, security_manager)

    proxy_class_hash = int(os.getenv("STARKNET_ARGENT_PROXY_HASH", "0x06d44f5b497e5222d3c6fe5158d3b73a575450575b99d2101c5c180d07bc318b"), 16)

    print(f"🚀 FINAL RESCUE ATTEMPT")
    print(f"🔑 Proxy Hash: {hex(proxy_class_hash)}")

    result = await engine.deploy_account_v3(
        class_hash=proxy_class_hash,
        salt=0,
        constructor_calldata=None,
    )

    if not result.get("success"):
        print(f"❌ Deployment failed: {result.get('error')}")
        print(f"💡 Alternative: portfolio.argent.xyz for manual recovery")
        return None

    print(f"� SUCCESS! Transaction: {result['tx_hash']}")
    print(f"� Deployed Address: {result.get('deployed_address')}")
    return result.get("tx_hash")


if __name__ == "__main__":
    asyncio.run(main())
