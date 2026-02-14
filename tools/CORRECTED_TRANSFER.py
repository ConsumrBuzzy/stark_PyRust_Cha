#!/usr/bin/env python3
"""
Corrected transfer with proper StarkNet address format
"""

import os
from pathlib import Path

def corrected_transfer():
    """Provide corrected transfer instructions"""
    print("🔧 CORRECTED TRANSFER INSTRUCTIONS")
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
    
    print(f"📍 From: {starknet_address}")
    print(f"🔑 Private Key: {private_key}")
    
    # The issue: Ready.co expects a StarkNet address, not Ethereum
    # Let's convert the Phantom address to StarkNet format
    phantom_ethereum = "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"
    
    print(f"\n❌ ISSUE: Ready.co expects StarkNet address format")
    print(f"❌ You provided Ethereum address: {phantom_ethereum}")
    
    print(f"\n✅ SOLUTION OPTIONS:")
    
    print(f"\n🎯 Option 1: Transfer to another StarkNet wallet first")
    print(f"1. Use Ready.co to import your account")
    print(f"2. Transfer to a working StarkNet wallet")
    print(f"3. Then bridge from that wallet to Base/Phantom")
    
    print(f"\n🎯 Option 2: Use a bridge that supports Ethereum addresses")
    print(f"1. Go to: https://rhino.fi/")
    print(f"2. Bridge from StarkNet to Base")
    print(f"3. Send to: {phantom_ethereum}")
    
    print(f"\n🎯 Option 3: Use Argent X")
    print(f"1. Download Argent X wallet")
    print(f"2. Import your private key")
    print(f"3. Send to Ethereum address")
    
    print(f"\n💰 Transfer Amount: 0.013863 ETH")
    print(f"🎯 Final Destination: {phantom_ethereum}")
    
    print(f"\n🔧 Why Ready.co rejected the address:")
    print(f"- Ready.co expects StarkNet address format")
    print(f"- Ethereum addresses need bridging, not direct transfer")
    print(f"- Use a bridge service that handles the conversion")

if __name__ == "__main__":
    corrected_transfer()
