#!/usr/bin/env python3
"""
Working StarkNet Deployment with Correct RPC
"""

import asyncio
import json
import aiohttp
from pathlib import Path

async def deploy_account():
    """Deploy account using working Mainnet RPC"""
    print("🚀 Working StarkNet Account Deployment")
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
    
    # Working Mainnet RPC
    rpc_url = "https://starknet-mainnet.public.blastapi.io"
    
    # Deploy account transaction for Mainnet v1
    payload = {
        "jsonrpc": "2.0",
        "method": "starknet_addDeployAccountTransaction",
        "params": {
            "deploy_account_transaction": {
                "type": "DEPLOY_ACCOUNT",
                "version": "0x1",
                "nonce": "0x0",
                "max_fee": "0x2386f26fc10000",
                "signature": [
                    "0x27cc2e9c10794a40bc0fe33dccc778e38b7af81220403a25d662f2ac50e52b1",
                    "0x2738c5963a046cafdc64d7105769e9d2a3e5a4d41b7eb57cbe7e0dd7dda97eb"
                ],
                "class_hash": "0x6d44f5b497e5222d3c6fe5158d3b73a575450575b99d2101c5c180d07bc318b",
                "contract_address_salt": "0x0",
                "constructor_calldata": [
                    "0x632d8e811cb6524d0f9381cd19ff4e809b3402fa79237261ac1f2e2cc2a4f31",
                    "0x0"
                ]
            }
        },
        "id": 1
    }
    
    try:
        print(f"🔥 Deploying to: {rpc_url}")
        
        headers = {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                rpc_url,
                headers=headers,
                data=json.dumps(payload)
            ) as response:
                result = await response.json()
                
                if 'error' in result:
                    print(f"❌ Error: {result['error']}")
                    return False
                
                if 'result' in result and 'transaction_hash' in result['result']:
                    tx_hash = result['result']['transaction_hash']
                    print(f"✅ SUCCESS! Transaction: {tx_hash}")
                    print("🎉 ACCOUNT DEPLOYED!")
                    print("💼 Ready for Influence game!")
                    return True
                
                print(f"❌ Unexpected response: {result}")
                return False
                
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    import os
    asyncio.run(deploy_account())
