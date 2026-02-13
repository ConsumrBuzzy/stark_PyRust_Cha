#!/usr/bin/env python3
"""
PyPro Systems - Instant Nonce Scanner
Get transaction hashes directly using nonce - NO BLOCK SCANNING
"""

import requests
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configuration
PHANTOM_ADDRESS = "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"
STARGATE_BRIDGE = "0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419"
ORBITER_BRIDGE = "0xe530d28960d48708CcF3e62Aa7B42A80bC427Aef"

# Fastest RPC endpoint
FAST_RPC = "https://base.gateway.tenderly.co"

def get_transaction_by_nonce(address: str, nonce: int) -> Dict[str, Any]:
    """Get transaction by specific nonce - INSTANT method"""
    try:
        # Method 1: Try to get transaction by nonce directly
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByBlockNumberAndIndex",
            "params": ["latest", nonce],
            "id": 1
        }
        
        response = requests.post(FAST_RPC, json=payload, timeout=3)
        data = response.json()
        
        if "result" in data and data["result"]:
            tx = data["result"]
            if tx["from"].lower() == address.lower():
                return parse_transaction(tx)
    except Exception:
        pass
    
    # Method 2: Use Etherscan API (if available)
    return get_transaction_by_etherscan(address)

def get_transaction_by_etherscan(address: str) -> Dict[str, Any]:
    """Get transaction using Etherscan API"""
    try:
        url = "https://api.basescan.org/api"
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "desc",
            "limit": 50
        }
        
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if data["status"] == "1":
            transactions = []
            for tx in data["result"]:
                parsed = parse_etherscan_tx(tx)
                if parsed:
                    transactions.append(parsed)
            return {"transactions": transactions}
        else:
            return {"error": data.get("result", "API error")}
            
    except Exception as e:
        return {"error": str(e)}

def parse_transaction(tx_data: Dict) -> Dict[str, Any]:
    """Parse transaction data"""
    try:
        from_addr = tx_data["from"]
        to_addr = tx_data.get("to", "")
        value = int(tx_data["value"], 16) / 1e18
        gas_price = int(tx_data.get("gasPrice", "0x0"), 16) / 1e9
        
        # Identify transaction type
        tx_type = "UNKNOWN"
        if to_addr:
            to_lower = to_addr.lower()
            if to_lower == STARGATE_BRIDGE.lower():
                tx_type = "STARKGATE_BRIDGE"
            elif to_lower == ORBITER_BRIDGE.lower():
                tx_type = "ORBITER_BRIDGE"
            else:
                tx_type = "CONTRACT_CALL"
        
        return {
            "hash": tx_data["hash"],
            "from": from_addr,
            "to": to_addr,
            "value": value,
            "type": tx_type,
            "gas_price_gwei": gas_price,
            "block_number": int(tx_data.get("blockNumber", "0x0"), 16),
            "nonce": int(tx_data.get("nonce", "0x0"), 16)
        }
    except Exception:
        return None

def parse_etherscan_tx(tx_data: Dict) -> Dict[str, Any]:
    """Parse Etherscan transaction data"""
    try:
        from_addr = tx_data["from"]
        to_addr = tx_data.get("to", "")
        value = float(tx_data["value"]) / 1e18
        gas_price = float(tx_data["gasPrice"]) / 1e9
        
        # Identify transaction type
        tx_type = "UNKNOWN"
        if to_addr:
            to_lower = to_addr.lower()
            if to_lower == STARGATE_BRIDGE.lower():
                tx_type = "STARKGATE_BRIDGE"
            elif to_lower == ORBITER_BRIDGE.lower():
                tx_type = "ORBITER_BRIDGE"
            else:
                tx_type = "CONTRACT_CALL"
        
        return {
            "hash": tx_data["hash"],
            "from": from_addr,
            "to": to_addr,
            "value": value,
            "type": tx_type,
            "gas_price_gwei": gas_price,
            "block_number": int(tx_data["blockNumber"]),
            "nonce": int(tx_data["nonce"]),
            "status": "success" if tx_data["isError"] == "0" else "failed",
            "timestamp": datetime.fromtimestamp(int(tx_data["timeStamp"])).isoformat()
        }
    except Exception:
        return None

def instant_nonce_analysis():
    """INSTANT analysis using nonce method"""
    print("⚡ INSTANT NONCE ANALYZER")
    print("=" * 40)
    
    start_time = time.time()
    
    # Step 1: Get current nonce
    print("📊 Getting wallet nonce...")
    
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionCount",
            "params": [PHANTOM_ADDRESS, "latest"],
            "id": 1
        }
        
        response = requests.post(FAST_RPC, json=payload, timeout=3)
        nonce = int(response.json()["result"], 16)
        
        print(f"   Nonce: {nonce} transactions")
        
    except Exception as e:
        print(f"❌ Failed to get nonce: {e}")
        return
    
    # Step 2: Get balance
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [PHANTOM_ADDRESS, "latest"],
            "id": 2
        }
        
        response = requests.post(FAST_RPC, json=payload, timeout=3)
        balance = int(response.json()["result"], 16) / 1e18
        
        print(f"   Balance: {balance:.6f} ETH")
        
    except Exception as e:
        print(f"❌ Failed to get balance: {e}")
        return
    
    # Step 3: Get transactions INSTANTLY
    print(f"\n🔍 Getting {nonce} transactions INSTANTLY...")
    
    # Use Etherscan API for instant results
    result = get_transaction_by_etherscan(PHANTOM_ADDRESS)
    
    if "error" in result:
        print(f"❌ API error: {result['error']}")
        return
    
    transactions = result.get("transactions", [])
    
    if not transactions:
        print("❌ No transactions found")
        return
    
    print(f"✅ Found {len(transactions)} transactions instantly!")
    
    # Step 4: Analyze transactions
    print(f"\n📋 TRANSACTION ANALYSIS")
    print("=" * 30)
    
    total_sent = 0.0
    bridge_count = 0
    total_gas_cost = 0.0
    
    for i, tx in enumerate(transactions, 1):
        total_sent += tx["value"]
        total_gas_cost += (tx["gas_price_gwei"] * 21000) / 1e9  # Rough gas cost
        
        if "BRIDGE" in tx["type"]:
            bridge_count += 1
        
        status_icon = "✅" if tx.get("status") == "success" else "❌"
        print(f"  {i}. {status_icon} {tx['hash'][:10]}... | {tx['value']:.6f} ETH | {tx['type']}")
        print(f"     Block: {tx['block_number']} | Nonce: {tx['nonce']}")
        print(f"     Time: {tx.get('timestamp', 'Unknown')[:19]}")
        print(f"     Explorer: https://basescan.org/tx/{tx['hash']}")
        print()
    
    # Step 5: Missing funds analysis
    print(f"💰 MISSING FUNDS ANALYSIS")
    print("=" * 30)
    
    expected_initial = 0.018
    current_balance = balance
    total_outflow = total_sent + total_gas_cost
    
    accounted_for = current_balance + total_outflow
    missing = expected_initial - accounted_for
    
    print(f"Expected (initial): {expected_initial:.6f} ETH")
    print(f"Current balance: {current_balance:.6f} ETH")
    print(f"Total sent: {total_sent:.6f} ETH")
    print(f"Gas costs: {total_gas_cost:.6f} ETH")
    print(f"Total outflow: {total_outflow:.6f} ETH")
    print(f"Accounted for: {accounted_for:.6f} ETH")
    print(f"Missing: {missing:.6f} ETH (${missing * 3500:.2f})")
    
    # Step 6: Bridge analysis
    if bridge_count > 0:
        print(f"\n🌉 BRIDGE ANALYSIS")
        print("=" * 20)
        
        bridge_txs = [tx for tx in transactions if "BRIDGE" in tx["type"]]
        bridge_total = sum(tx["value"] for tx in bridge_txs)
        
        print(f"Bridge transactions: {bridge_count}")
        print(f"Total bridged: {bridge_total:.6f} ETH")
        
        for tx in bridge_txs:
            print(f"  {tx['hash'][:10]}... | {tx['value']:.6f} ETH | {tx['type']}")
        
        # Check if bridge amounts explain missing funds
        if abs(bridge_total - missing) < 0.001:
            print(f"\n✅ Bridge amounts match missing funds!")
            print(f"🔍 Funds likely stuck in bridge contracts")
            print(f"💡 NEXT STEP: Check bridge contract status")
        else:
            print(f"\n⚠️  Bridge total ({bridge_total:.6f}) ≠ missing ({missing:.6f})")
            print(f"🔍 Additional investigation needed")
    
    # Step 7: Instant recommendations
    print(f"\n🎯 INSTANT RECOMMENDATIONS")
    print("=" * 30)
    
    if bridge_count > 0:
        print("🔴 URGENT: Check bridge contracts for stuck funds")
        print("   Command: python tools/check_bridge_status.py")
        print()
        print("🟡 MEDIUM: Monitor StarkNet address for received funds")
        print("   Command: python tools/check_starknet_balance.py")
        print()
        print("🟢 LOW: Use remaining funds for partial activation")
        print(f"   Available: {balance:.6f} ETH")
    else:
        print("🟡 Funds likely consumed by gas fees and failed operations")
        print("🟢 Add more funds to continue operations")
    
    analysis_time = time.time() - start_time
    print(f"\n⚡ INSTANT analysis completed in {analysis_time:.2f} seconds")
    
    # Save results
    report = {
        "timestamp": datetime.now().isoformat(),
        "analysis_time_seconds": analysis_time,
        "method": "INSTANT_NONCE_API",
        "current_balance": balance,
        "nonce": nonce,
        "transactions_found": len(transactions),
        "total_sent": total_sent,
        "gas_costs": total_gas_cost,
        "missing_funds": missing,
        "bridge_count": bridge_count,
        "transactions": transactions
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/reports/instant_nonce_{timestamp}.json"
    
    report_path = Path(output_file)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    
    print(f"\n📄 Report saved to: {output_file}")
    
    return report

def main():
    instant_nonce_analysis()

if __name__ == "__main__":
    main()
