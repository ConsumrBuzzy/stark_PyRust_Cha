#!/usr/bin/env python3
"""
Transfer all StarkNet funds back to Phantom wallet
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.ops.audit_ops import run_audit

def transfer_to_phantom():
    """Transfer all funds to Phantom wallet"""
    print("🚀 Transfer All Funds to Phantom")
    print("=" * 40)
    
    # Load environment
    env_path = Path(__file__).parent.parent / ".env"
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key.strip()] = value.strip()
    
    starknet_address = os.getenv("STARKNET_WALLET_ADDRESS")
    phantom_address = "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"
    
    print(f"📍 From: {starknet_address}")
    print(f"📍 To: {phantom_address}")
    
    # Get current balance using audit tool
    try:
        # Run audit to get balance
        result = asyncio.run(run_audit(
            ghost_address="0x000000000000000000000000ff01e0776369ce51debb16dfb70f23c16d875463",
            main_address=starknet_address
        ))
        
        balance_eth = float(result.main_balance_eth)
        print(f"💰 Current Balance: {balance_eth:.6f} ETH")
        
        if balance_eth < 0.001:
            print("❌ Balance too low for transfer")
            return False
        
        # Calculate transfer amount (leave small amount for gas)
        transfer_amount = balance_eth - 0.001  # Leave 0.001 ETH for gas
        print(f"💸 Transfer Amount: {transfer_amount:.6f} ETH")
        
        # Create transfer instructions
        print(f"\n🔧 Transfer Instructions:")
        print(f"1. Go to Ready.co: https://web.ready.co/")
        print(f"2. Import private key: 0632d8e811cb6524d0f9381cd19ff4e809b3402fa79237261ac1f2e2cc2a4f31")
        print(f"3. Send {transfer_amount:.6f} ETH to: {phantom_address}")
        print(f"4. Keep 0.001 ETH for gas fees")
        
        # Alternative: Bridge instructions
        print(f"\n🌉 Alternative - Bridge to Base:")
        print(f"1. Use Rhino.fi: https://rhino.fi/")
        print(f"2. Bridge from StarkNet to Base")
        print(f"3. Send to: {phantom_address}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    transfer_to_phantom()
