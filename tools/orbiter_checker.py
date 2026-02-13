"""
Orbiter Bridge Checker - L1 Transaction Status
============================================
Checks if the 0.006 ETH is stuck in the Orbiter bridge contract
"""

import os
import asyncio
from web3 import Web3
from starknet_py.net.full_node_client import FullNodeClient

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
    ghost_address = "os.getenv("STARKNET_GHOST_ADDRESS")"
    
    print(f"\n👻 StarkNet Ghost Address: {ghost_address}")
    try:
        client = FullNodeClient(node_url=os.getenv("STARKNET_MAINNET_URL"))
        
        from starknet_py.hash.selector import get_selector_from_name
        from starknet_py.net.client_models import Call
        
        eth_address = "int(os.getenv("STARKNET_ETH_CONTRACT", "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"), 16)"
        call = Call(
            to_addr=int(eth_address, 16),
            selector=get_selector_from_name("balanceOf"),
            calldata=[int(ghost_address, 16)]
        )
        
        result = await client.call_contract(call)
        balance = result[0] / 10**18
        
        print(f"💰 Ghost Balance: {balance:.6f} ETH")
        
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
