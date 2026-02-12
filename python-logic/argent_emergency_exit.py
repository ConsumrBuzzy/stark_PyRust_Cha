"""
Argent Emergency Exit - Final Stand Protocol
==========================================
Deploys Argent Web Wallet to unlock trapped funds
"""

import os
import asyncio
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

async def exit_protocol():
    """Final attempt to deploy Argent Web Wallet"""
    
    # 1. AUTHENTICATION
    private_key_str = os.getenv("STARKNET_PRIVATE_KEY")
    target_addr_str = os.getenv("STARKNET_WALLET_ADDRESS")
    rpc_url = os.getenv("STARKNET_MAINNET_URL")
    
    if not all([private_key_str, target_addr_str, rpc_url]):
        print("❌ Missing required environment variables")
        return
    
    private_key = int(private_key_str, 16)
    target_addr = int(target_addr_str, 16)
    
    print(f"🚀 EMERGENCY EXIT PROTOCOL")
    print(f"🎯 Target: {hex(target_addr)}")
    print(f"🔑 Key: {private_key_str[:20]}...")
    
    # 2. ARGENT WEB PARAMETERS
    ARGENT_CLASS_HASH = 0x01a7366993b74e484c2fa434313f89832207b53f609e25d26a27a26a27a26a27
    
    client = FullNodeClient(node_url=rpc_url)
    key_pair = KeyPair.from_private_key(private_key)

    # 3. RESOURCE BOUNDS (ETH for fees)
    resource_bounds = ResourceBoundsMapping(
        l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
        l1_data_gas=ResourceBounds(max_amount=int(1e4), max_price_per_unit=int(1e13)),
        l2_gas=ResourceBounds(max_amount=int(1e9), max_price_per_unit=int(1e17))
    )

    # 4. ATTEMPT DEPLOYMENT
    try:
        print("🔧 Attempting Argent Web deployment...")
        
        # Try salt=0 first (most common for Argent Web)
        result = await Account.deploy_account_v3(
            address=target_addr,
            class_hash=ARGENT_CLASS_HASH,
            salt=0,
            key_pair=key_pair,
            client=client,
            constructor_calldata=[key_pair.public_key, 0],  # Owner + Guardian(0)
            resource_bounds=resource_bounds,
        )
        
        print(f"✅ EXFILTRATION STARTED: {hex(result.hash)}")
        print(f"🔗 Starkscan: https://starkscan.co/tx/{hex(result.hash)}")
        
        # Wait for confirmation
        print("⌛ Waiting for deployment confirmation...")
        await result.wait_for_acceptance()
        print("🎉 SUCCESS! Account is now active.")
        
        return result.hash
        
    except Exception as e:
        print(f"❌ Salt 0 failed: {e}")
        
        # Try salt=1 as fallback
        try:
            print("🔄 Trying salt=1...")
            result = await Account.deploy_account_v3(
                address=target_addr,
                class_hash=ARGENT_CLASS_HASH,
                salt=1,
                key_pair=key_pair,
                client=client,
                constructor_calldata=[key_pair.public_key, 0],
                resource_bounds=resource_bounds,
            )
            
            print(f"✅ EXFILTRATION STARTED (salt=1): {hex(result.hash)}")
            await result.wait_for_acceptance()
            print("🎉 SUCCESS! Account is now active.")
            
            return result.hash
            
        except Exception as e2:
            print(f"❌ Salt 1 failed: {e2}")
            print("💀 Both deployment attempts failed.")
            print("🌐 Alternative: Visit portfolio.argent.xyz for manual recovery")
            return None

if __name__ == "__main__":
    asyncio.run(exit_protocol())
