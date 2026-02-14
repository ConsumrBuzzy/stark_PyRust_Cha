#!/usr/bin/env python3
"""
Get Real Gas Prices from Block Data
"""

import asyncio
import json
import aiohttp
from pathlib import Path

async def get_real_gas():
    """Get real gas prices from latest block"""
    print("🔍 Getting Real Gas Prices from Block Data")
    print("=" * 50)
    
    # Working RPC
    rpc_url = "https://1rpc.io/starknet"
    
    try:
        headers = {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            # Get latest block
            block_payload = {
                "jsonrpc": "2.0",
                "method": "starknet_getBlockWithTxs",
                "params": [{"block_number": "latest"}],
                "id": 1
            }
            
            async with session.post(
                rpc_url,
                headers=headers,
                data=json.dumps(block_payload),
                timeout=15
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if 'result' in result:
                        block = result['result']
                        print(f"✅ Block {block.get('block_number', 'unknown')}")
                        
                        # Look for transactions with gas info
                        if 'transactions' in block:
                            for i, tx in enumerate(block['transactions'][:3]):  # First 3 txs
                                if 'max_fee' in tx:
                                    max_fee = int(tx['max_fee'], 16)
                                    fee_eth = max_fee / 1e18
                                    print(f"💰 Tx {i+1} fee: {fee_eth:.6f} ETH")
                        
                        # Get gas price from block if available
                        if 'l1_gas_price' in block:
                            l1_gas_price = int(block['l1_gas_price'], 16)
                            gwei = l1_gas_price / 1e9
                            print(f"⛽ L1 Gas Price: {gwei:.2f} Gwei")
                        
                        if 'l2_gas_price' in block:
                            l2_gas_price = int(block['l2_gas_price'], 16)
                            gwei = l2_gas_price / 1e9
                            print(f"⛽ L2 Gas Price: {gwei:.2f} Gwei")
                        
                        # Try deploy with real gas prices
                        print(f"\n🚀 Testing deployment with real gas prices...")
                        
                        # Use real gas price if available
                        real_gas_price = block.get('l1_gas_price', '0x59682f00')  # Default 10 Gwei
                        
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
                                            "max_price_per_unit": real_gas_price
                                        },
                                        "l1_data_gas": {
                                            "max_amount": "0x186a0",
                                            "max_price_per_unit": real_gas_price
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
                        
                        async with session.post(
                            rpc_url,
                            headers=headers,
                            data=json.dumps(deploy_payload),
                            timeout=15
                        ) as deploy_response:
                            deploy_result = await deploy_response.json()
                            
                            if 'error' in deploy_result:
                                print(f"❌ Deploy error: {deploy_result['error']}")
                            else:
                                print(f"✅ Deploy success: {deploy_result}")
                    else:
                        print(f"❌ Block error: {result}")
                else:
                    print(f"❌ HTTP {response.status}")
                    
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(get_real_gas())
