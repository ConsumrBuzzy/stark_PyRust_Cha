#!/usr/bin/env python3
"""
Simple transfer script to move funds back to Phantom
"""

import asyncio
import os
import json
import aiohttp
from pathlib import Path

async def transfer_funds():
    """Transfer funds from StarkNet to Phantom"""
    print("🚀 Transfer Funds to Phantom")
    print("=" * 30)
    
    # Load environment
    env_path = Path(__file__).parent.parent / ".env"
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key.strip()] = value.strip()
    
    starknet_address = os.getenv("STARKNET_WALLET_ADDRESS")
    phantom_address = "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"
    
    print(f"From: {starknet_address}")
    print(f"To: {phantom_address}")
    
    # Use working RPC
    rpc_url = "https://1rpc.io/starknet"
    
    try:
        headers = {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            # Get balance
            payload = {
                "jsonrpc": "2.0",
                "method": "starknet_getBalance",
                "params": [
                    {
                        "contract_address": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
                        "block_number": "latest"
                    },
                    starknet_address
                ],
                "id": 1
            }
            
            async with session.post(rpc_url, headers=headers, data=json.dumps(payload)) as response:
                result = await response.json()
                
                if 'result' in result:
                    balance_wei = int(result['result'], 16)
                    balance_eth = balance_wei / 1e18
                    print(f"Balance: {balance_eth:.6f} ETH")
                    
                    # Create transfer transaction (simplified)
                    print("Creating transfer transaction...")
                    print("Note: This requires manual signing with private key")
                    print(f"Transfer all but 0.001 ETH to Phantom")
                    
                    return True
                else:
                    print(f"Error: {result}")
                    
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(transfer_funds())
