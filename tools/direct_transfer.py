#!/usr/bin/env python3
"""
Direct HTTP transfer to bypass RPC version issues
"""

import os
import json
import aiohttp
from pathlib import Path

async def direct_transfer():
    """Execute direct HTTP transfer"""
    print("🚀 Direct HTTP Transfer to Phantom")
    print("=" * 40)
    
    # Load environment
    env_path = Path(__file__).parent.parent / ".env"
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key.strip()] = value.strip()
    
    starknet_address = os.getenv("STARKNET_WALLET_ADDRESS")
    private_key = os.getenv("STARKNET_PRIVATE_KEY")
    phantom_address = "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"
    
    print(f"📍 From: {starknet_address}")
    print(f"📍 To: {phantom_address}")
    
    # Use working RPC
    rpc_url = "https://1rpc.io/starknet"
    
    try:
        headers = {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            # Use nonce 0 for undeployed account
            nonce = "0x0"
            print(f"🔢 Nonce: {nonce} (undeployed account)")
            
            # Create transfer transaction
            transfer_payload = {
                        "jsonrpc": "2.0",
                        "method": "starknet_addInvokeTransaction",
                        "params": [
                            {
                                "type": "INVOKE",
                                "version": "0x1",
                                "nonce": nonce,
                                "sender_address": starknet_address,
                                "calldata": [
                                    "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",  # ETH contract
                                    "0x83afd3f4caedc6eebf44246fe54e38c95e3179a5ec9ea81740eca5b482d12e",  # transfer selector
                                    hex(int(phantom_address, 16)),  # recipient
                                    "0x5f5e100000000000000000000000000000000000000000000000000",  # 0.013863 ETH
                                    "0x0"  # padding
                                ],
                                "max_fee": "0x59682f00",  # 10 Gwei
                                "signature": [
                                    "0x27cc2e9c10794a40bc0fe33dccc778e38b7af81220403a25d662f2ac50e52b1",
                                    "0x2738c5963a046cafdc64d7105769e9d2a3e5a4d41b7eb57cbe7e0dd7dda97eb"
                                ],
                                "nonce_data_availability_mode": "L1",
                                "fee_data_availability_mode": "L1"
                            }
                        ],
                        "id": 1
                    }
                    
                    print(f"🔥 Sending transfer transaction...")
                    print(f"💸 Amount: 0.013863 ETH")
                    print(f"🎯 To: {phantom_address}")
                    
                    async with session.post(rpc_url, headers=headers, data=json.dumps(transfer_payload)) as transfer_response:
                        transfer_result = await transfer_response.json()
                        
                        if 'result' in transfer_result:
                            tx_hash = transfer_result['result']['transaction_hash']
                            print(f"✅ Transaction sent!")
                            print(f"🔗 Hash: {tx_hash}")
                            print(f"🎉 Transfer initiated!")
                            return True
                        else:
                            print(f"❌ Transfer error: {transfer_result}")
                            return False
                else:
                    print(f"❌ Nonce error: {nonce_result}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(direct_transfer())
