#!/usr/bin/env python3
"""
Compare Multiple RPC Endpoints
"""

import asyncio
import json
import aiohttp

async def test_all_endpoints():
    """Test all available endpoints"""
    print("🔍 Comparing All RPC Endpoints")
    print("=" * 40)
    
    endpoints = [
        ("1RPC", "https://1rpc.io/starknet"),
        ("OnFinality", "https://starknet.api.onfinality.io/public"),
        ("dRPC", "https://starknet.drpc.org"),
        ("Lava", "https://rpc.starknet.lava.build"),
        ("QuickNode Demo", "https://docs-demo.strk-mainnet.quiknode.pro"),
    ]
    
    for name, rpc_url in endpoints:
        print(f"\n🔥 Testing {name}: {rpc_url}")
        
        try:
            headers = {"Content-Type": "application/json"}
            async with aiohttp.ClientSession() as session:
                # Test basic connectivity
                payload = {
                    "jsonrpc": "2.0",
                    "method": "starknet_blockNumber",
                    "params": [],
                    "id": 1
                }
                
                async with session.post(rpc_url, headers=headers, data=json.dumps(payload), timeout=10) as response:
                    if response.status == 200:
                        result = await response.json()
                        if 'result' in result:
                            print(f"✅ Connected - Block: {result['result']}")
                            
                            # Test pending transactions for fee info
                            pending_payload = {
                                "jsonrpc": "2.0",
                                "method": "starknet_pendingTransactions",
                                "params": [],
                                "id": 1
                            }
                            
                            async with session.post(rpc_url, headers=headers, data=json.dumps(pending_payload), timeout=10) as pending_response:
                                if pending_response.status == 200:
                                    pending_result = await pending_response.json()
                                    if 'result' in pending_result:
                                        tx_count = len(pending_result['result'])
                                        print(f"📊 Pending txs: {tx_count}")
                                        
                                        # Look at first tx for fee
                                        if tx_count > 0:
                                            first_tx = pending_result['result'][0]
                                            if 'max_fee' in first_tx:
                                                max_fee = int(first_tx['max_fee'], 16)
                                                fee_eth = max_fee / 1e18
                                                print(f"💰 First tx fee: {fee_eth:.6f} ETH")
                                                
                                                # Estimate gas price
                                                if 'version' in first_tx:
                                                    version = first_tx['version']
                                                    print(f"📝 Tx version: {version}")
                                    else:
                                        print(f"❌ Pending tx error: {pending_result}")
                                else:
                                    print(f"❌ Pending tx HTTP {pending_response.status}")
                        else:
                            print(f"❌ Block error: {result}")
                    else:
                        print(f"❌ HTTP {response.status}")
                        
        except Exception as e:
            print(f"❌ Failed: {str(e)[:50]}")
    
    print(f"\n🎯 Summary: Working endpoints with real data")

if __name__ == "__main__":
    asyncio.run(test_all_endpoints())
