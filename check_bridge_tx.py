#!/usr/bin/env python3
"""
Check Phantom bridge transaction status
"""

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

def check_bridge_transaction():
    """Check the StarkGate bridge transaction"""
    
    # Connect to Base
    w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    
    tx_hash = '0x2dfc79aa3ad0ba437b7122a2b538eb72b2259f261a3f40818e7fa7a5074a64cd'
    starkgate_address = '0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419'
    
    print("🔍 PHANTOM BRIDGE TRANSACTION ANALYSIS")
    print("=" * 50)
    
    try:
        # Check transaction receipt
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        tx = w3.eth.get_transaction(tx_hash)
        
        print(f"📋 Transaction Details:")
        print(f"   Hash: {tx_hash}")
        print(f"   Status: {'✅ SUCCESS' if receipt.status == 1 else '❌ FAILED'}")
        print(f"   Block: {receipt.blockNumber}")
        print(f"   Gas Used: {receipt.gasUsed:,}")
        print(f"   Gas Limit: {tx.gas:,}")
        print(f"   Value: {w3.from_wei(tx.value, 'ether')} ETH")
        print(f"   From: {tx['from']}")
        print(f"   To: {tx.to}")
        
        # Check if sent to StarkGate
        if tx.to.lower() == starkgate_address.lower():
            print(f"   ✅ Correctly sent to StarkGate bridge")
        else:
            print(f"   ❌ WRONG RECIPIENT: Expected {starkgate_address}")
        
        # Check logs for bridge events
        print(f"\n📜 Transaction Logs:")
        for i, log in enumerate(receipt.logs):
            print(f"   Log {i}:")
            print(f"     Address: {log.address}")
            print(f"     Topics: {log.topics[:1]}...")  # First topic only
            print(f"     Data: {log.data[:50]}...")  # First 50 chars
        
        # Check if transaction was successful
        if receipt.status == 1:
            print(f"\n✅ Transaction SUCCESSFUL on Base network")
            print(f"🔄 Bridge should be processing on StarkNet...")
        else:
            print(f"\n❌ Transaction FAILED on Base network")
            print(f"🚨 Bridge never initiated")
            
    except Exception as e:
        print(f"❌ Error checking transaction: {e}")

if __name__ == "__main__":
    check_bridge_transaction()
