#!/usr/bin/env python3
"""
Test Real RPC Endpoints for Actual Gas Prices
"""

import asyncio
import json
import aiohttp
from pathlib import Path

async def test_real_rpcs():
    """Test multiple RPC endpoints for real data"""
    print("🔍 Testing Real RPC Endpoints")
    print("=" * 40)
    
    # Real RPC endpoints (not demo)
    rpc_urls = [
        "https://starknet-mainnet.public.blastapi.io",
        "https://rpc.starknet.lava.build",
        "https://1rpc.io/starknet",
        "https://starknet.api.onfinality.io/public",
        "https://docs-demo.strk-mainnet.quiknode.pro",  # Control
    ]
    
    # Test payload for gas price
    payload = {
        "jsonrpc": "2.0",
        "method": "starknet_blockNumber",
        "params": [],
        "id": 1
    }
    
    for rpc_url in rpc_urls:
        try:
            print(f"\n🔥 Testing: {rpc_url}")
            
            headers = {"Content-Type": "application/json"}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    rpc_url,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=10
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if 'result' in result:
                            block_number = result['result']
                            print(f"✅ Connected - Block: {block_number}")
                            
                            # Test gas price
                            gas_payload = {
                                "jsonrpc": "2.0", 
                                "method": "starknet_gasPrice",
                                "params": [],
                                "id": 1
                            }
                            
                            async with session.post(
                                rpc_url,
                                headers=headers,
                                data=json.dumps(gas_payload),
                                timeout=10
                            ) as gas_response:
                                if gas_response.status == 200:
                                    gas_result = await gas_response.json()
                                    if 'result' in gas_result:
                                        gas_price = int(gas_result['result'], 16)
                                        gwei = gas_price / 1e9
                                        print(f"⛽ Gas Price: {gwei:.2f} Gwei")
                                    else:
                                        print(f"❌ Gas price error: {gas_result}")
                                else:
                                    print(f"❌ Gas price failed: {gas_response.status}")
                        else:
                            print(f"❌ Block error: {result}")
                    else:
                        print(f"❌ HTTP {response.status}")
                        
        except Exception as e:
            print(f"❌ Failed: {str(e)[:50]}")
    
    print(f"\n🎯 Recommendation: Use the working endpoint with normal gas prices")

if __name__ == "__main__":
    asyncio.run(test_real_rpcs())
