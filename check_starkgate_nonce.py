#!/usr/bin/env python3
"""
Check StarkGate message nonce status
"""

import asyncio
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from starknet_py.net.full_node_client import FullNodeClient

async def check_starkgate_nonce():
    """Check StarkGate message nonce and L1→L2 status"""
    
    print("🔍 STARGATE MESSAGE NONCE ANALYSIS")
    print("=" * 50)
    
    # Connect to Base
    w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    
    # Connect to StarkNet
    starknet_client = FullNodeClient(node_url='https://starknet-mainnet.g.alchemy.com/starknet/version/rpc/v0_10/9HtNv_yFeMgWsbW_gI2IN')
    
    tx_hash = '0x2dfc79aa3ad0ba437b7122a2b538eb72b2259f261a3f40818e7fa7a5074a64cd'
    starkgate_address = '0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419'
    
    try:
        # Get transaction details
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        print(f"📋 Base Transaction:")
        print(f"   Hash: {tx_hash}")
        print(f"   Block: {receipt.blockNumber}")
        print(f"   Status: {'✅ CONFIRMED' if receipt.status == 1 else '❌ FAILED'}")
        
        # Check logs for message nonce
        print(f"\n🔍 Message Queue Analysis:")
        
        # StarkGate bridge event signature (simplified)
        bridge_topic = "0x"  # Would need actual event signature
        
        message_found = False
        for i, log in enumerate(receipt.logs):
            if log.address.lower() == starkgate_address.lower():
                print(f"   📜 Log {i}: Potential bridge message")
                print(f"      Data: {log.data}")
                print(f"      Topics: {len(log.topics)} topics")
                message_found = True
        
        if not message_found:
            print("   ⚠️  No bridge logs found in transaction")
        
        # Check current StarkNet balance
        try:
            from starknet_py.hash.selector import get_selector_from_name
            from starknet_py.net.client_models import Call
            
            call = Call(
                to_addr=int("0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7", 16),
                selector=get_selector_from_name("balanceOf"),
                calldata=[int("0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9", 16)]
            )
            
            result = await starknet_client.call_contract(call)
            current_balance = result[0] / 1e18
            
            print(f"\n💰 Current StarkNet Balance: {current_balance:.6f} ETH")
            print(f"🎯 Activation Threshold: 0.018 ETH")
            print(f"📊 Still Need: {0.018 - current_balance:.6f} ETH")
            
        except Exception as e:
            print(f"❌ Balance check failed: {e}")
        
        # Recommendation
        print(f"\n🎯 RECOMMENDATION:")
        if current_balance < 0.018:
            print(f"   ⏳ Wait for first bridge (0.009 ETH) to arrive")
            print(f"   💰 Then sweep remaining Phantom balance (0.0047 ETH)")
            print(f"   🎯 Total expected: {current_balance + 0.009 + 0.0047:.6f} ETH")
        else:
            print(f"   ✅ Sufficient balance for activation!")
            
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_starkgate_nonce())
