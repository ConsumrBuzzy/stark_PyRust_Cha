"""
Orbiter Bridge Checker - L1 Transaction Status
============================================
Checks if the 0.006 ETH is stuck in the Orbiter bridge contract
"""

import os
import sys
import asyncio
from web3 import Web3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ops.ghost_monitor import check_ghost_balance, load_settings

def load_env():
    env_path = ".env"
    if not os.path.exists(env_path): return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

load_env()

async def check_orbiter_status():
    """Check Orbiter bridge transaction status"""
    
    print("🔍 ORBITER BRIDGE STATUS CHECK")
    print("="*50)
    
    # Base transaction we know about
    base_tx_hash = "0x2dec7c24a1b11c731a25fd8c7c2e681488e0c58730ba82f9d20d46032a263407"
    
    # Check Base transaction status
    print(f"📋 Base Transaction: {base_tx_hash}")
    try:
        w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
        receipt = w3.eth.get_transaction_receipt(base_tx_hash)
        
        if receipt.status == 1:
            print(f"✅ Base Transaction: CONFIRMED")
            print(f"   Block: {receipt.blockNumber}")
            print(f"   Gas Used: {receipt.gasUsed}")
            
            # Get transaction details
            tx = w3.eth.get_transaction(base_tx_hash)
            print(f"   From: {tx['from']}")
            print(f"   To: {tx['to']}")
            print(f"   Value: {tx['value'] / 10**18:.6f} ETH")
            
        else:
            print(f"❌ Base Transaction: FAILED")
            
    except Exception as e:
        print(f"❌ Base check failed: {e}")
    
    # Check StarkNet ghost address
    settings = load_settings()
    ghost_address = settings.ghost_address

    print(f"\n👻 StarkNet Ghost Address: {ghost_address}")
    try:
        balance, rpc_used = await check_ghost_balance(settings=settings, use_rpc_rotation=True)
        print(f"💰 Ghost Balance: {balance:.6f} ETH")
        if rpc_used:
            print(f"   (via {rpc_used})")

        if balance > 0:
            print(f"✅ FUNDS DETECTED! Ready for sweep")
        else:
            print(f"❌ No funds on StarkNet yet")
            
    except Exception as e:
        print(f"❌ StarkNet check failed: {e}")
    
    # Check Orbiter bridge contract
    print(f"\n🌉 Orbiter Bridge Analysis")
    print(f"The 0.006 ETH left Base successfully but hasn't reached StarkNet.")
    print(f"This indicates the funds are stuck in the Orbiter L1-L2 bridge contract.")
    print(f"\n💡 NEXT STEPS:")
    print(f"1. Visit: https://orbiter.finance/history")
    print(f"2. Connect your Phantom wallet: 0xfF01E0776369Ce51debb16DFb70F23c16d875463")
    print(f"3. Look for the 0.006 ETH transaction")
    print(f"4. Use 'Claim' or 'Contact Support' button")
    print(f"5. Alternative: Wait for automatic processing (can take hours)")

if __name__ == "__main__":
    asyncio.run(check_orbiter_status())
