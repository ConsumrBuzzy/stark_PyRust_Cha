"""
Final Rescue Attempt - Proxy Hash Deployment
==========================================
Uses the discovered Argent Proxy class hash to unlock funds
"""

import os
import asyncio
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.models import StarknetChainId
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

async def main():
    """Final deployment attempt with discovered proxy hash"""
    
    # Configuration
    rpc_url = os.getenv("STARKNET_MAINNET_URL")
    private_key_str = os.getenv("STARKNET_PRIVATE_KEY")
    target_addr_str = os.getenv("STARKNET_WALLET_ADDRESS")
    
    if not all([rpc_url, private_key_str, target_addr_str]):
        print("❌ Missing required environment variables")
        return
    
    # The discovered Argent Proxy class hash
    proxy_class_hash = 0x06d44f5b497e5222d3c6fe5158d3b73a575450575b99d2101c5c180d07bc318b
    pk = int(private_key_str, 16)
    target = int(target_addr_str, 16)
    
    client = FullNodeClient(node_url=rpc_url)
    key_pair = KeyPair.from_private_key(pk)

    print(f"🚀 FINAL RESCUE ATTEMPT")
    print(f"🎯 Target: {hex(target)}")
    print(f"🔑 Proxy Hash: {hex(proxy_class_hash)}")
    print(f"👤 Public Key: {hex(key_pair.public_key)}")
    
    # Resource bounds for ETH fees
    resource_bounds = ResourceBoundsMapping(
        l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
        l1_data_gas=ResourceBounds(max_amount=int(1e4), max_price_per_unit=int(1e13)),
        l2_gas=ResourceBounds(max_amount=int(1e9), max_price_per_unit=int(1e17))
    )
    
    print(f"\n📡 Attempting Force-Deployment with Proxy Hash...")
    
    try:
        # Deploy with salt=0 (Ready.co default)
        result = await Account.deploy_account_v3(
            address=target,
            class_hash=proxy_class_hash,
            salt=0,
            key_pair=key_pair,
            client=client,
            constructor_calldata=[key_pair.public_key, 0],
            resource_bounds=resource_bounds,
        )
        
        print(f"🚀 SUCCESS! Transaction: {hex(result.hash)}")
        print(f"🔗 Starkscan: https://starkscan.co/tx/{hex(result.hash)}")
        
        # Wait for confirmation
        print("⌛ Waiting for deployment confirmation...")
        await result.wait_for_acceptance()
        print("🎉 ACCOUNT DEPLOYED! Funds are now unlocked!")
        
        # Check balance after deployment
        from starknet_py.hash.selector import get_selector_from_name
        from starknet_py.net.client_models import Call
        
        eth_address = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
        call = Call(
            to_addr=int(eth_address, 16),
            selector=get_selector_from_name("balanceOf"),
            calldata=[target]
        )
        
        balance_result = await client.call_contract(call)
        balance = balance_result[0] / 10**18
        
        print(f"💰 Account Balance: {balance:.6f} ETH")
        print(f"💵 Value: ${balance * 2200:.2f} USD")  # Assuming $2200/ETH
        
        return result.hash
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        print(f"💡 Alternative: portfolio.argent.xyz for manual recovery")
        return None

if __name__ == "__main__":
    asyncio.run(main())
