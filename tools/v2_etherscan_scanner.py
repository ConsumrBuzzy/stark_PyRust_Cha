#!/usr/bin/env python3
"""
PyPro Systems - Etherscan V2 API Scanner
Migrated to Etherscan API V2 with proper chainid support
"""

import requests
import json
import sys
import time
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configuration
PHANTOM_ADDRESS = "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"
STARKNET_MAIN = "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
STARKNET_GHOST = "0x000000000000000000000000ff01e0776369ce51debb16dfb70f23c16d875463"

# Bridge contracts
STARGATE_BRIDGE = "0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419"
ORBITER_BRIDGE = "0xe530d28960d48708CcF3e62Aa7B42A80bC427Aef"

# V2 API Configuration
V2_BASE_URL = "https://api.etherscan.io/v2/api"
BASE_CHAIN_ID = "8453"  # Base network chain ID

# API Key (you can get one from https://etherscan.io/apidashboard)
API_KEY = os.getenv("ETHERSCAN_API_KEY", "YourEtherscanApiKey")

def make_v2_api_call(action: str, address: str = None, **params) -> Dict[str, Any]:
    """Make Etherscan V2 API call"""
    try:
        url = V2_BASE_URL
        
        # Base parameters for V2 API
        api_params = {
            "chainid": BASE_CHAIN_ID,
            "action": action,
            "apikey": API_KEY
        }
        
        # Add address if provided
        if address:
            api_params["address"] = address
        
        # Add additional parameters
        api_params.update(params)
        
        response = requests.get(url, params=api_params, timeout=10)
        data = response.json()
        
        if data["status"] == "1":
            return {"success": True, "data": data["result"]}
        else:
            return {"success": False, "error": data.get("result", "Unknown V2 API error")}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_balance_v2(address: str) -> Dict[str, Any]:
    """Get balance using V2 API"""
    result = make_v2_api_call("balance", address=address)
    
    if result["success"]:
        balance_wei = int(result["data"])
        balance_eth = balance_wei / 1e18
        
        return {
            "success": True,
            "address": address,
            "balance_wei": balance_wei,
            "balance_eth": balance_eth,
            "balance_usd": balance_eth * 3500
        }
    else:
        return {"success": False, "address": address, "error": result["error"]}

def get_transactions_v2(address: str, limit: int = 50) -> Dict[str, Any]:
    """Get transactions using V2 API"""
    result = make_v2_api_call(
        "txlist", 
        address=address,
        startblock=0,
        endblock=99999999,
        sort="desc",
        limit=limit
    )
    
    if result["success"]:
        transactions = []
        for tx in result["data"]:
            # Parse transaction data
            from_addr = tx["from"]
            to_addr = tx.get("to", "")
            value = float(tx["value"]) / 1e18
            gas_price = float(tx["gasPrice"]) / 1e9
            
            # Identify transaction type
            tx_type = "UNKNOWN"
            if to_addr:
                to_lower = to_addr.lower()
                if to_lower == STARGATE_BRIDGE.lower():
                    tx_type = "STARGATE_BRIDGE"
                elif to_lower == ORBITER_BRIDGE.lower():
                    tx_type = "ORBITER_BRIDGE"
                else:
                    tx_type = "CONTRACT_CALL"
            
            transactions.append({
                "hash": tx["hash"],
                "from": from_addr,
                "to": to_addr,
                "value": value,
                "type": tx_type,
                "gas_price_gwei": gas_price,
                "block_number": int(tx["blockNumber"]),
                "nonce": int(tx["nonce"]),
                "status": "success" if tx["isError"] == "0" else "failed",
                "timestamp": datetime.fromtimestamp(int(tx["timeStamp"])).isoformat(),
                "confirmations": int(tx["confirmations"])
            })
        
        return {"success": True, "transactions": transactions}
    else:
        return {"success": False, "error": result["error"]}

def analyze_missing_funds_v2():
    """Analyze missing funds using V2 API"""
    print("🚀 ETHERSCAN V2 API SCANNER")
    print("=" * 40)
    
    # Check API key
    if API_KEY == "YourEtherscanApiKey":
        print("⚠️  No API key found!")
        print("📝 Get one from: https://etherscan.io/apidashboard")
        print("💡 Set environment variable: ETHERSCAN_API_KEY=your_key_here")
        print()
        print("🔄 Trying without API key (limited requests)...")
    
    start_time = time.time()
    
    # Step 1: Get balances for all addresses
    print("📊 Step 1: Getting balances...")
    
    addresses = [PHANTOM_ADDRESS, STARKNET_MAIN, STARKNET_GHOST]
    balances = {}
    
    for addr in addresses:
        print(f"   Checking {addr[:10]}...")
        result = get_balance_v2(addr)
        
        if result["success"]:
            balances[addr] = result
            print(f"   ✅ {result['balance_eth']:.6f} ETH (${result['balance_usd']:.2f})")
        else:
            balances[addr] = {"success": False, "balance_eth": 0.0, "error": result["error"]}
            print(f"   ❌ Error: {result['error']}")
    
    # Step 2: Get Phantom transactions
    print(f"\n🔍 Step 2: Getting Phantom transactions...")
    
    phantom_result = get_transactions_v2(PHANTOM_ADDRESS, limit=20)
    
    if not phantom_result["success"]:
        print(f"❌ Failed to get transactions: {phantom_result['error']}")
        return
    
    transactions = phantom_result["transactions"]
    print(f"✅ Found {len(transactions)} transactions")
    
    # Step 3: Analyze transactions
    print(f"\n📋 Step 3: Transaction analysis...")
    
    total_sent = 0.0
    bridge_count = 0
    total_gas_cost = 0.0
    bridge_transactions = []
    
    for i, tx in enumerate(transactions, 1):
        total_sent += tx["value"]
        total_gas_cost += (tx["gas_price_gwei"] * 21000) / 1e9  # Rough gas cost
        
        if "BRIDGE" in tx["type"]:
            bridge_count += 1
            bridge_transactions.append(tx)
        
        status_icon = "✅" if tx["status"] == "success" else "❌"
        print(f"  {i}. {status_icon} {tx['hash'][:10]}... | {tx['value']:.6f} ETH | {tx['type']}")
        print(f"     Block: {tx['block_number']} | Nonce: {tx['nonce']}")
        print(f"     Time: {tx['timestamp'][:19]}")
        print(f"     Explorer: https://basescan.org/tx/{tx['hash']}")
        print()
    
    # Step 4: Missing funds analysis
    print(f"💰 Step 4: Missing funds analysis...")
    
    phantom_balance = balances[PHANTOM_ADDRESS].get("balance_eth", 0.0)
    starknet_balance = balances[STARKNET_MAIN].get("balance_eth", 0.0)
    ghost_balance = balances[STARKNET_GHOST].get("balance_eth", 0.0)
    
    total_current = phantom_balance + starknet_balance + ghost_balance
    expected_initial = 0.018
    total_outflow = total_sent + total_gas_cost
    
    accounted_for = total_current + total_outflow
    missing = expected_initial - accounted_for
    
    print(f"Expected (initial): {expected_initial:.6f} ETH")
    print(f"Current total: {total_current:.6f} ETH")
    print(f"  Phantom: {phantom_balance:.6f} ETH")
    print(f"  StarkNet: {starknet_balance:.6f} ETH")
    print(f"  Ghost: {ghost_balance:.6f} ETH")
    print(f"Total sent: {total_sent:.6f} ETH")
    print(f"Gas costs: {total_gas_cost:.6f} ETH")
    print(f"Total outflow: {total_outflow:.6f} ETH")
    print(f"Accounted for: {accounted_for:.6f} ETH")
    print(f"Missing: {missing:.6f} ETH (${missing * 3500:.2f})")
    
    # Step 5: Bridge analysis
    if bridge_count > 0:
        print(f"\n🌉 Step 5: Bridge analysis...")
        
        bridge_total = sum(tx["value"] for tx in bridge_transactions)
        
        print(f"Bridge transactions: {bridge_count}")
        print(f"Total bridged: {bridge_total:.6f} ETH")
        
        for tx in bridge_transactions:
            print(f"  {tx['hash'][:10]}... | {tx['value']:.6f} ETH | {tx['type']}")
            print(f"    Status: {tx['status']} | Time: {tx['timestamp'][:19]}")
        
        # Check if bridge amounts explain missing funds
        if abs(bridge_total - missing) < 0.001:
            print(f"\n✅ Bridge amounts match missing funds!")
            print(f"🔍 Funds likely stuck in bridge contracts")
            print(f"💡 NEXT STEP: Check bridge contract status")
        else:
            print(f"\n⚠️  Bridge total ({bridge_total:.6f}) ≠ missing ({missing:.6f})")
            print(f"🔍 Additional investigation needed")
    
    # Step 6: Recommendations
    print(f"\n🎯 Step 6: Recommendations...")
    
    if missing > 0.01:
        print("🔴 HIGH PRIORITY:")
        if bridge_count > 0:
            print("   1. Check bridge contracts for stuck funds")
            print("   2. Monitor StarkNet address for received funds")
        print("   3. Use remaining funds for partial activation")
        print(f"      Available: {phantom_balance:.6f} ETH")
        print(f"      Needed for activation: ~0.003 ETH")
    elif bridge_count > 0:
        print("🟡 MEDIUM PRIORITY:")
        print("   1. Monitor bridge transactions for completion")
        print("   2. Check StarkNet address for received funds")
    else:
        print("🟢 LOW PRIORITY:")
        print("   1. Funds accounted for")
        print("   2. Consider adding more funds for operations")
    
    analysis_time = time.time() - start_time
    print(f"\n⚡ V2 API analysis completed in {analysis_time:.2f} seconds")
    
    # Save results
    report = {
        "timestamp": datetime.now().isoformat(),
        "api_version": "V2",
        "analysis_time_seconds": analysis_time,
        "balances": balances,
        "transactions_found": len(transactions),
        "total_sent": total_sent,
        "gas_costs": total_gas_cost,
        "missing_funds": missing,
        "bridge_count": bridge_count,
        "bridge_transactions": bridge_transactions,
        "all_transactions": transactions
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/reports/v2_analysis_{timestamp}.json"
    
    report_path = Path(output_file)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    
    print(f"\n📄 Report saved to: {output_file}")
    
    return report

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test V2 API
        print("🧪 Testing V2 API...")
        
        result = make_v2_api_call("balance", address=PHANTOM_ADDRESS)
        if result["success"]:
            balance = int(result["data"]) / 1e18
            print(f"✅ V2 API works! Balance: {balance:.6f} ETH")
        else:
            print(f"❌ V2 API error: {result['error']}")
        return
    
    analyze_missing_funds_v2()

if __name__ == "__main__":
    main()
