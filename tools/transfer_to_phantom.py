#!/usr/bin/env python3
"""
Transfer all StarkNet funds back to Phantom wallet
"""

import asyncio
import os
import json
import aiohttp
from pathlib import Path

async def transfer_to_phantom():
    """Transfer all funds from StarkNet to Phantom"""
    print("🚀 Transferring All Funds to Phantom")
    print("=" * 40)
    
    # Load environment
    env_path = Path(__file__).parent.parent / ".env"
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key.strip()] = value.strip()
    
    # Configuration
    starknet_address = os.getenv("STARKNET_WALLET_ADDRESS")
    starknet_private_key = os.getenv("STARKNET_PRIVATE_KEY")
    phantom_address = "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"
    
    print(f"📍 From: {starknet_address}")
    print(f"📍 To: {phantom_address}")
    
    # Use working RPC endpoint
    rpc_url = "https://1rpc.io/starknet"
    
    try:
        headers = {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            # Get current balance
            balance_payload = {
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
            
            async with session.post(rpc_url, headers=headers, data=json.dumps(balance_payload)) as response:
                balance_result = await response.json()
                
                if 'result' in balance_result:
                    balance_wei = int(balance_result['result'], 16)
                    balance_eth = balance_wei / 1e18
                    print(f"💰 Current Balance: {balance_eth:.6f} ETH")
                    
                    if balance_eth < 0.001:
                        print("❌ Balance too low for transfer")
                        return False
                    
                    # Calculate transfer amount (leave small amount for gas)
                    transfer_amount = balance_wei - int(0.0005e18)  # Leave 0.0005 ETH for gas
                    transfer_eth = transfer_amount / 1e18
                    print(f"💸 Transfer Amount: {transfer_eth:.6f} ETH")
                    
                    # Get nonce
                    nonce_payload = {
                        "jsonrpc": "2.0",
                        "method": "starknet_getNonce",
                        "params": [
                            {
                                "block_number": "latest"
                            },
                            starknet_address
                        ],
                        "id": 1
                    }
                    
                    async with session.post(rpc_url, headers=headers, data=json.dumps(nonce_payload)) as nonce_response:
                        nonce_result = await nonce_response.json()
                        
                        if 'result' in nonce_result:
                            nonce = int(nonce_result['result'], 16)
                            print(f"🔢 Nonce: {nonce}")
                            
                            # Create transfer transaction
                            transfer_payload = {
                                "jsonrpc": "2.0",
                                "method": "starknet_addInvokeTransaction",
                                "params": [
                                    {
                                        "type": "INVOKE",
                                        "version": "0x1",
                                        "nonce": hex(nonce),
                                        "sender_address": starknet_address,
                                        "calldata": [
                                            "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",  # ETH contract
                                            "0x83afd3f4caedc6eebf44246fe54e38c95e3179a5ec9ea81740eca5b482d12e",  # transfer selector
                                            hex(int(phantom_address, 16)),  # recipient
                                            hex(transfer_amount),  # amount
                                            "0x0"  # padding
                                        ],
                                        "max_fee": "0x59682f00",  # 10 Gwei
                                        "signature": [],
                                        "nonce_data_availability_mode": "L1",
                                        "fee_data_availability_mode": "L1"
                                    }
                                ],
                                "id": 1
                            }
                            
                            print(f"🔥 Creating transfer transaction...")
                            print(f"📋 Transfer: {transfer_eth:.6f} ETH to Phantom")
                            
                            # Note: This would need signing with private key
                            # For now, just show the transaction structure
                            print(f"⚠️  Transaction created (needs signing)")
                            print(f"📝 To complete: Sign with private key and submit")
                            
                            return True
                        else:
                            print(f"❌ Nonce error: {nonce_result}")
                        else:
                            print(f"❌ Balance error: {balance_result}")
                            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(transfer_to_phantom())
