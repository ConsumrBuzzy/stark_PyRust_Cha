import asyncio
import os
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

load_env()

from starknet_py.hash.address import compute_address

async def main():
    # 1. AUTHENTICATION (Zero-Inference from .env)
    rpc_url = os.getenv("STARKNET_MAINNET_URL")
    private_key_str = os.getenv("STARKNET_PRIVATE_KEY")
    target_address_str = os.getenv("STARKNET_WALLET_ADDRESS")
    
    if not private_key_str or not target_address_str:
        print("❌ Missing STARKNET_PRIVATE_KEY or STARKNET_WALLET_ADDRESS in .env")
        return
    
    private_key = int(private_key_str, 16)
    target_address = int(target_address_str, 16)
    
    client = FullNodeClient(node_url=rpc_url)
    key_pair = KeyPair.from_private_key(private_key)

    # Calculate the correct salt for this address
    class_hash = 0x0539f522860b093c83664d4c5709968853f3e828d57d740f941f1738722a4501
    computed_address = compute_address(
        class_hash=class_hash,
        constructor_calldata=[key_pair.public_key],
        salt=0,
        deployer_address=0
    )
    
    print(f"Target address: {hex(target_address)}")
    print(f"Computed address: {hex(computed_address)}")
    
    if computed_address != target_address:
        print("❌ Address mismatch. This account was created with a different class_hash or salt.")
        print("⚠️ Cannot deploy. The account may already exist with different parameters.")
        return

    # 2. RESOURCE BOUNDS (The "Confused Currency" Fix)
    # We set these to use ETH for fees during deployment
    resource_bounds = ResourceBoundsMapping(
        l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
        l1_data_gas=ResourceBounds(max_amount=int(1e4), max_price_per_unit=int(1e13)),
        l2_gas=ResourceBounds(max_amount=int(1e9), max_price_per_unit=int(1e17))
    )

    print(f"🚀 Broadcasting Deployment for {hex(target_address)}...")

    # 3. STATIC DEPLOYMENT (Bypasses 'Account' object initialization)
    try:
        deploy_result = await Account.deploy_account_v3(
            address=target_address,
            class_hash=0x0539f522860b093c83664d4c5709968853f3e828d57d740f941f1738722a4501, # Standard OZ Account
            salt=0, 
            key_pair=key_pair,
            client=client,
            constructor_calldata=[key_pair.public_key],
            resource_bounds=resource_bounds,
        )
        
        print(f"✅ Transaction Hash: {hex(deploy_result.hash)}")
        print("⌛ Waiting for L2 Acceptance...")
        await deploy_result.wait_for_acceptance()
        print("🎉 SUCCESS. Account is now active on Starknet.")

    except Exception as e:
        print(f"❌ Deployment Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
