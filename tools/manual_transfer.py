#!/usr/bin/env python3
"""
Manual transfer instructions with transaction data
"""

import os
import json
from pathlib import Path

def create_manual_transfer():
    """Create manual transfer transaction data"""
    print("🚀 Manual Transfer Transaction Creator")
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
    print(f"🔑 Private Key: {private_key}")
    
    # Create transfer transaction data
    transfer_data = {
        "type": "INVOKE",
        "version": "0x1",
        "sender_address": starknet_address,
        "calldata": [
            "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",  # ETH contract
            "0x83afd3f4caedc6eebf44246fe54e38c95e3179a5ec9ea81740eca5b482d12e",  # transfer selector
            hex(int(phantom_address, 16)),  # recipient
            "0x5f5e100000000000000000000000000000000000000000000000000",  # 0.013863 ETH in wei
            "0x0"  # padding
        ],
        "max_fee": "0x59682f00",  # 10 Gwei
        "nonce": "0x0",
        "signature": [],
        "nonce_data_availability_mode": "L1",
        "fee_data_availability_mode": "L1"
    }
    
    print(f"\n📋 Transaction Data:")
    print(json.dumps(transfer_data, indent=2))
    
    print(f"\n🔧 Manual Transfer Steps:")
    print(f"1. Go to StarkScan: https://starkscan.io/")
    print(f"2. Search your address: {starknet_address}")
    print(f"3. Click 'Send Transaction'")
    print(f"4. Use the transaction data above")
    print(f"5. Sign with your private key")
    print(f"6. Submit transaction")
    
    print(f"\n💰 Amount: 0.013863 ETH")
    print(f"🎯 Recipient: {phantom_address}")
    print(f"⛽ Max Fee: 10 Gwei")
    
    return transfer_data

if __name__ == "__main__":
    create_manual_transfer()
