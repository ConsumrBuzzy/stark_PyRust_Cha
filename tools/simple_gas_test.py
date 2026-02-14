#!/usr/bin/env python3
"""
Simple Real Gas Test
"""

import asyncio
import json
import aiohttp

async def test_simple_gas():
    """Test with simple block call"""
    print("🔍 Simple Real Gas Test")
    print("=" * 30)
    
    rpc_url = "https://1rpc.io/starknet"
    
    try:
        headers = {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            # Try simple block number first
            payload = {
                "jsonrpc": "2.0",
                "method": "starknet_blockNumber",
                "params": [],
                "id": 1
            }
            
            async with session.post(rpc_url, headers=headers, data=json.dumps(payload)) as response:
                result = await response.json()
                print(f"Block number: {result}")
                
                # Try pending transactions
                pending_payload = {
                    "jsonrpc": "2.0",
                    "method": "starknet_pendingTransactions",
                    "params": [],
                    "id": 1
                }
                
                async with session.post(rpc_url, headers=headers, data=json.dumps(pending_payload)) as pending_response:
                    pending_result = await pending_response.json()
                    print(f"Pending txs: {len(pending_result.get('result', []))}")
                    
                    # Look at first pending tx for gas info
                    if 'result' in pending_result and pending_result['result']:
                        first_tx = pending_result['result'][0]
                        if 'max_fee' in first_tx:
                            max_fee = int(first_tx['max_fee'], 16)
                            fee_eth = max_fee / 1e18
                            print(f"First tx fee: {fee_eth:.6f} ETH")
                            
                            # Calculate approximate gas price
                            if 'version' in first_tx and first_tx['version'] == '0x3':
                                print("✅ Found v0.3 transaction")
                                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_gas())
