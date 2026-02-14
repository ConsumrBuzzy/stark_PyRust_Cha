#!/usr/bin/env python3
"""
Deploy with Realistic Gas Prices
"""

import asyncio
import json
import aiohttp
from pathlib import Path

async def deploy_realistic():
    """Deploy with realistic gas prices"""
    print("🚀 Realistic Gas Price Deployment")
    print("=" * 40)
    
    # Load environment
    env_path = Path(__file__).parent.parent / ".env"
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key.strip()] = value.strip()
    
    wallet_address = os.getenv("STARKNET_WALLET_ADDRESS")
    private_key = os.getenv("STARKNET_PRIVATE_KEY")
    
    print(f"📍 Address: {wallet_address}")
    print(f"💰 Balance: 0.014863 ETH")
    
    # Use working 1RPC endpoint
    rpc_url = "https://1rpc.io/starknet"
    
    # Realistic gas prices (not demo inflated)
    payload = {
        "jsonrpc": "2.0",
        "method": "starknet_addDeployAccountTransaction",
        "params": [
            {
                "type": "DEPLOY_ACCOUNT",
                "version": "0x3",
                "nonce": "0x0",
                "signature": [
                    "0x27cc2e9c10794a40bc0fe33dccc778e38b7af81220403a25d662f2ac50e52b1",
                    "0x2738c5963a046cafdc64d7105769e9d2a3e5a4d41b7eb57cbe7e0dd7dda97eb"
                ],
                "contract_address_salt": "0x0",
                "class_hash": "0x6d44f5b497e5222d3c6fe5158d3b73a575450575b99d2101c5c180d07bc318b",
                "constructor_calldata": [
                    "0x632d8e811cb6524d0f9381cd19ff4e809b3402fa79237261ac1f2e2cc2a4f31",
                    "0x0"
                ],
                "resource_bounds": {
                    "l1_gas": {
                        "max_amount": "0x186a0",
                        "max_price_per_unit": "0x59682f00"  # 10 Gwei
                    },
                    "l1_data_gas": {
                        "max_amount": "0x186a0",
                        "max_price_per_unit": "0x59682f00"  # 10 Gwei
                    },
                    "l2_gas": {
                        "max_amount": "0x88b80",
                        "max_price_per_unit": "0x59682f00"  # 10 Gwei
                    }
                },
                "tip": "0x0",
                "paymaster_data": [],
                "nonce_data_availability_mode": "L1",
                "fee_data_availability_mode": "L1"
            }
        ],
        "id": 1
    }
    
    try:
        print(f"🔥 Deploying to: {rpc_url}")
        print(f"⛽ Using realistic gas: 10 Gwei")
        
        headers = {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                rpc_url,
                headers=headers,
                data=json.dumps(payload)
            ) as response:
                result = await response.json()
                
                if 'error' in result:
                    error = result['error']
                    print(f"❌ Error: {error}")
                    
                    # If gas price too low, try higher
                    if 'gas price' in str(error).lower():
                        print(f"⛽ Gas too low, trying 50 Gwei...")
                        
                        # Update to higher gas price
                        payload['params'][0]['resource_bounds']['l1_gas']['max_price_per_unit'] = "0x2b5d3c8000"  # 50 Gwei
                        payload['params'][0]['resource_bounds']['l1_data_gas']['max_price_per_unit'] = "0x2b5d3c8000"
                        
                        async with session.post(
                            rpc_url,
                            headers=headers,
                            data=json.dumps(payload)
                        ) as retry_response:
                            retry_result = await retry_response.json()
                            if 'error' in retry_result:
                                print(f"❌ Retry error: {retry_result['error']}")
                            else:
                                print(f"✅ SUCCESS! {retry_result}")
                    else:
                        print(f"❌ Other error: {error}")
                else:
                    print(f"✅ SUCCESS! Transaction: {result}")
                    
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    import os
    asyncio.run(deploy_realistic())
