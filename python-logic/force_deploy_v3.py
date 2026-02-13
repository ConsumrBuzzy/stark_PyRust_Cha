import asyncio
import os
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
    load_env_manual()

    network_oracle = NetworkOracle()
    security_manager = SecurityManager()
    engine = DeploymentEngine(network_oracle, security_manager)

    result = await engine.deploy_account_v3()

    if result.get("success"):
        print(f"✅ Transaction Hash: {result['tx_hash']}")
        print(f"Deployed Address: {result.get('deployed_address')}")
    else:
        print(f"❌ Deployment Failed: {result.get('error')}")
        if result.get("computed_address"):
            print(f"Computed Address: {result['computed_address']}")


if __name__ == "__main__":
    asyncio.run(main())
