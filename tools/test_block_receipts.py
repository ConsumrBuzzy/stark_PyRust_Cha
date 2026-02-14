#!/usr/bin/env python3
"""
Test Block with Receipts for Gas Data
"""

import asyncio
import json
import aiohttp

async def test_block_receipts():
    """Test block with receipts for gas data"""
    print("🔍 Testing Block with Receipts")
    print("=" * 35)
    
    rpc_url = "https://starknet.drpc.org"
    
    try:
        headers = {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            # Get block with receipts
            payload = {
                "jsonrpc": "2.0",
                "method": "starknet_getBlockWithReceipts",
                "params": [{"block_number": "latest"}],
                "id": 1
            }
            
            async with session.post(rpc_url, headers=headers, data=json.dumps(payload)) as response:
                result = await response.json()
                
                if 'result' in result:
                    block = result['result']
                    print(f"✅ Block {block.get('block_number', 'unknown')}")
                    
                    # Look for gas info in block
                    if 'l1_gas_price' in block:
                        l1_gas_price = int(block['l1_gas_price'], 16)
                        gwei = l1_gas_price / 1e9
                        print(f"⛽ L1 Gas Price: {gwei:.2f} Gwei")
                    
                    # Look at transactions for fees
                    if 'transactions' in block and block['transactions']:
                        for i, tx in enumerate(block['transactions'][:3]):
                            if 'max_fee' in tx:
                                max_fee = int(tx['max_fee'], 16)
                                fee_eth = max_fee / 1e18
                                print(f"💰 Tx {i+1} fee: {fee_eth:.6f} ETH")
                            
                            if 'actual_fee' in tx:
                                actual_fee = int(tx['actual_fee'], 16)
                                fee_eth = actual_fee / 1e18
                                print(f"💸 Tx {i+1} actual: {fee_eth:.6f} ETH")
                        
                        # Try deployment with real gas
                        if 'l1_gas_price' in block:
                            real_gas = block['l1_gas_price']
                            
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
                                                "max_price_per_unit": real_gas
                                            },
                                            "l1_data_gas": {
                                                "max_amount": "0x186a0",
                                                "max_price_per_unit": real_gas
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
                            
                            print(f"\n🚀 Trying deployment with real gas...")
                            async with session.post(rpc_url, headers=headers, data=json.dumps(deploy_payload)) as deploy_response:
                                deploy_result = await deploy_response.json()
                                print(f"🚀 Deploy result: {deploy_result}")
                    else:
                        print(f"❌ No transactions in block")
                else:
                    print(f"❌ Block error: {result}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_block_receipts())
