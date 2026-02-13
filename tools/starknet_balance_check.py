#!/usr/bin/env python3
"""
PyPro Systems - StarkNet Balance Checker
Direct RPC calls to check if bridge funds arrived
"""

import requests
import json
import sys
from pathlib import Path
from datetime import datetime

# Configuration
STARKNET_ADDRESS = "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
STARKNET_ETH_CONTRACT = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"

# StarkNet RPC endpoints
STARKNET_RPCS = [
    "https://starknet-mainnet.g.alchemy.com/starknet/version/rpc/v0_10/demo",  # Demo
    "https://starknet-mainnet.public.blastapi.io/rpc/v0.7",  # Public
    "https://rpc.starknet.liskl.com/",  # Alternative
]

def make_starknet_call(rpc_url: str, method: str, params: list = None) -> dict:
    """Make StarkNet RPC call"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
            "id": 1
        }
        
        response = requests.post(rpc_url, json=payload, timeout=10)
        data = response.json()
        
        if "error" in data:
            return {"error": data["error"]}
        return {"result": data["result"]}
        
    except Exception as e:
        return {"error": str(e)}

def get_starknet_balance() -> dict:
    """Get ETH balance on StarkNet"""
    print("🔍 CHECKING STARKNET BALANCE")
    print("=" * 40)
    
    for rpc_url in STARKNET_RPCS:
        print(f"📡 Trying: {rpc_url}")
        
        # Method 1: Get ETH balance directly
        result = make_starknet_call(
            rpc_url, 
            "starknet_call", 
            [
                {
                    "contract_address": STARKNET_ETH_CONTRACT,
                    "entry_point_selector": "0x02e4b86b825620c8b432393fda5604d7566c91408b2d7b276a42d9fd86ca7263",  # balanceOf
                    "calldata": [STARKNET_ADDRESS]
                },
                "latest"
            ]
        )
        
        if "error" not in result:
            balance_raw = result["result"][0]  # First element is the balance
            balance_eth = int(balance_raw, 16) / 1e18
            
            print(f"✅ SUCCESS! Balance: {balance_eth:.6f} ETH")
            return {
                "success": True,
                "balance_eth": balance_eth,
                "balance_usd": balance_eth * 3500,
                "rpc_used": rpc_url
            }
        else:
            print(f"❌ Error: {result['error']}")
    
    return {"success": False, "error": "All RPCs failed"}

def check_transaction_status(tx_hash: str) -> dict:
    """Check transaction status on StarkNet"""
    print(f"\n🔍 CHECKING TRANSACTION STATUS")
    print("=" * 40)
    print(f"Hash: {tx_hash}")
    
    for rpc_url in STARKNET_RPCS:
        print(f"📡 Trying: {rpc_url}")
        
        result = make_starknet_call(rpc_url, "starknet_getTransactionReceipt", [tx_hash])
        
        if "error" not in result:
            receipt = result["result"]
            
            status = receipt.get("status", "UNKNOWN")
            block_number = receipt.get("block_number", "PENDING")
            
            print(f"✅ Transaction found!")
            print(f"   Status: {status}")
            print(f"   Block: {block_number}")
            
            # Parse events to see if ETH was transferred
            events = receipt.get("events", [])
            for event in events:
                if event.get("from_address") == STARKNET_ETH_CONTRACT:
                    print(f"   📝 ETH Contract Event: {event}")
            
            return {
                "success": True,
                "status": status,
                "block_number": block_number,
                "events": events,
                "rpc_used": rpc_url
            }
        else:
            print(f"❌ Error: {result['error']}")
    
    return {"success": False, "error": "Transaction not found"}

def check_account_deployed() -> dict:
    """Check if StarkNet account is deployed"""
    print(f"\n🔍 CHECKING ACCOUNT DEPLOYMENT")
    print("=" * 40)
    print(f"Address: {STARKNET_ADDRESS}")
    
    for rpc_url in STARKNET_RPCS:
        print(f"📡 Trying: {rpc_url}")
        
        # Get class hash at address
        result = make_starknet_call(rpc_url, "starknet_getClassHashAt", [STARKNET_ADDRESS, "latest"])
        
        if "error" not in result:
            class_hash = result["result"]
            
            if class_hash == "0x0":
                print(f"❌ Account NOT deployed")
                return {"success": True, "deployed": False, "class_hash": None}
            else:
                print(f"✅ Account IS deployed")
                print(f"   Class Hash: {class_hash}")
                return {"success": True, "deployed": True, "class_hash": class_hash}
        else:
            print(f"❌ Error: {result['error']}")
    
    return {"success": False, "error": "Could not determine deployment status"}

def main():
    print("🚀 STARKNET BRIDGE FUNDS CHECKER")
    print("=" * 50)
    print(f"Target Address: {STARKNET_ADDRESS}")
    print(f"ETH Contract: {STARKNET_ETH_CONTRACT}")
    print()
    
    # Check 1: Account deployment status
    account_status = check_account_deployed()
    
    # Check 2: Balance
    balance_result = get_starknet_balance()
    
    # Check 3: Transaction status (if we have the hash)
    starknet_tx_hash = "0x2dfc79aa3ad0ba437b7122a2b538eb72b2259f261a3f40818e7fa7a5074a64cd"
    tx_status = check_transaction_status(starknet_tx_hash)
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("=" * 20)
    
    if balance_result["success"]:
        print(f"💰 Balance: {balance_result['balance_eth']:.6f} ETH (${balance_result['balance_usd']:.2f})")
        
        if balance_result["balance_eth"] > 0.008:  # Close to bridge amount
            print(f"✅ BRIDGE SUCCESS! Funds arrived on StarkNet")
            print(f"🎯 Your 0.009 ETH bridge completed successfully")
        elif balance_result["balance_eth"] > 0:
            print(f"⚠️  Partial funds arrived ({balance_result['balance_eth']:.6f} ETH)")
        else:
            print(f"❌ No funds detected on StarkNet")
            print(f"🔍 Bridge may still be processing or failed")
    else:
        print(f"❌ Could not check balance: {balance_result['error']}")
    
    if tx_status["success"]:
        print(f"📋 Transaction Status: {tx_status['status']}")
        if tx_status["status"] == "ACCEPTED_ON_L2":
            print(f"✅ Transaction accepted on StarkNet")
        else:
            print(f"⚠️  Transaction status: {tx_status['status']}")
    else:
        print(f"❌ Could not check transaction: {tx_status['error']}")
    
    if account_status["success"]:
        if account_status["deployed"]:
            print(f"✅ Account deployed - ready for operations")
        else:
            print(f"❌ Account not deployed - needs activation")
            print(f"💡 Use remaining funds to deploy account")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/reports/starknet_check_{timestamp}.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "starknet_address": STARKNET_ADDRESS,
        "balance_result": balance_result,
        "transaction_status": tx_status,
        "account_status": account_status
    }
    
    report_path = Path(output_file)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    
    print(f"\n📄 Report saved to: {output_file}")

if __name__ == "__main__":
    main()
