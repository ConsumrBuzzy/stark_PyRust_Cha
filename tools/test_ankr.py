#!/usr/bin/env python3
"""
Test Ankr RPC Endpoint
"""

import asyncio
import json
import aiohttp

async def test_ankr():
    """Test Ankr RPC endpoint"""
    print("🔍 Testing Ankr RPC Endpoint")
    print("=" * 30)
    
    # Ankr StarkNet endpoint
    rpc_url = "https://rpc.ankr.com/starknet"
    
    try:
        headers = {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            # Test block number
            payload = {
                "jsonrpc": "2.0",
                "method": "starknet_blockNumber",
                "params": [],
                "id": 1
            }
            
            async with session.post(rpc_url, headers=headers, data=json.dumps(payload)) as response:
                result = await response.json()
                print(f"Block number: {result}")
                
                # Test gas price
                gas_payload = {
                    "jsonrpc": "2.0",
                    "method": "starknet_gasPrice",
                    "params": [],
                    "id": 1
                }
                
                async with session.post(rpc_url, headers=headers, data=json.dumps(gas_payload)) as gas_response:
                    gas_result = await gas_response.json()
                    print(f"Gas price result: {gas_result}")
                    
                    if 'result' in gas_result:
                        gas_price = int(gas_result['result'], 16)
                        gwei = gas_price / 1e9
                        print(f"⛽ Ankr Gas Price: {gwei:.2f} Gwei")
                        
                        # Try deployment with Ankr gas price
                        deploy_payload = {
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
                                            "max_price_per_unit": gas_result['result']
                                        },
                                        "l1_data_gas": {
                                            "max_amount": "0x186a0",
                                            "max_price_per_unit": gas_result['result']
                                        },
                                        "l2_gas": {
                                            "max_amount": "0x88b80",
                                            "max_price_per_unit": "0x59682f00"
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
                        
                        async with session.post(rpc_url, headers=headers, data=json.dumps(deploy_payload)) as deploy_response:
                            deploy_result = await deploy_response.json()
                            print(f"🚀 Ankr Deploy result: {deploy_result}")
                    else:
                        print(f"❌ Gas price error: {gas_result}")
                        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ankr())
