#!/usr/bin/env python3
"""
PyPro Systems - Hyper Fast Scanner
Ultra-fast transaction discovery using optimized block ranges
"""

import requests
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
PHANTOM_ADDRESS = "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"
STARGATE_BRIDGE = "0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419"
ORBITER_BRIDGE = "0xe530d28960d48708CcF3e62Aa7B42A80bC427Aef"

# Ultra-fast RPC endpoint
FAST_RPC = "https://base.gateway.tenderly.co"

def make_batch_rpc_calls(calls: List[Dict]) -> List[Dict]:
    """Make multiple RPC calls in parallel"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_call",
            "params": calls,
            "id": 1
        }
        
        response = requests.post(FAST_RPC, json=payload, timeout=5)
        data = response.json()
        
        return data.get("result", [])
    except Exception as e:
        print(f"Batch call failed: {e}")
        return []

def get_current_block() -> int:
    """Get current block number"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        }
        
        response = requests.post(FAST_RPC, json=payload, timeout=3)
        data = response.json()
        
        return int(data["result"], 16)
    except Exception:
        return 0

def scan_block_range(start_block: int, end_block: int, target_address: str) -> List[Dict]:
    """Scan a specific block range for transactions"""
    transactions = []
    
    for block_num in range(start_block, end_block + 1):
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBlockByNumber",
                "params": [hex(block_num), True],
                "id": 1
            }
            
            response = requests.post(FAST_RPC, json=payload, timeout=2)
            data = response.json()
            
            if "result" in data and data["result"]:
                block = data["result"]
                
                for tx in block.get("transactions", []):
                    if (tx["from"].lower() == target_address.lower() and 
                        tx["value"] != "0x0"):
                        
                        value = int(tx["value"], 16) / 1e18
                        to_addr = tx.get("to", "")
                        
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
                        
                        transactions.append({
                            "hash": tx["hash"],
                            "from": tx["from"],
                            "to": to_addr,
                            "value": value,
                            "block": block_num,
                            "type": tx_type,
                            "gas_price": int(tx.get("gasPrice", "0x0"), 16) / 1e9,
                            "input": tx.get("input", "")[:20]
                        })
                        
                        print(f"✅ Found: {tx['hash'][:10]}... | {value:.6f} ETH | {tx_type}")
                        
        except Exception:
            continue
    
    return transactions

def hyper_fast_scan():
    """Hyper-fast transaction scanning"""
    print("⚡ HYPER FAST TRANSACTION SCANNER")
    print("=" * 50)
    
    start_time = time.time()
    
    # Step 1: Get current state
    print("📊 Getting current state...")
    
    try:
        # Get current balance and nonce
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [PHANTOM_ADDRESS, "latest"],
            "id": 1
        }
        
        response = requests.post(FAST_RPC, json=payload, timeout=3)
        balance = int(response.json()["result"], 16) / 1e18
        
        payload["method"] = "eth_getTransactionCount"
        response = requests.post(FAST_RPC, json=payload, timeout=3)
        nonce = int(response.json()["result"], 16)
        
        print(f"   Balance: {balance:.6f} ETH")
        print(f"   Nonce: {nonce} transactions")
        
    except Exception as e:
        print(f"❌ Failed to get state: {e}")
        return
    
    # Step 2: Smart block range detection
    print(f"\n🔍 Smart block range detection...")
    
    current_block = get_current_block()
    if current_block == 0:
        print("❌ Failed to get current block")
        return
    
    # Strategy: Transactions are likely in recent blocks, but we need to search wider
    # Use exponential search to find the right range
    
    print(f"   Current block: {current_block}")
    
    # Search strategy: check multiple ranges in parallel
    search_ranges = [
        (current_block - 1000, current_block),      # Very recent
        (current_block - 5000, current_block - 1000), # Recent
        (current_block - 10000, current_block - 5000), # Medium
        (current_block - 20000, current_block - 10000), # Older
    ]
    
    all_transactions = []
    
    print(f"   Scanning {len(search_ranges)} ranges in parallel...")
    
    # Use ThreadPoolExecutor for parallel scanning
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all range scans
        future_to_range = {
            executor.submit(scan_block_range, start, end, PHANTOM_ADDRESS): (start, end)
            for start, end in search_ranges
        }
        
        # Collect results
        for future in as_completed(future_to_range):
            start, end = future_to_range[future]
            try:
                transactions = future.result(timeout=30)
                if transactions:
                    print(f"   ✅ Range {start}-{end}: Found {len(transactions)} transactions")
                    all_transactions.extend(transactions)
                else:
                    print(f"   ⭕ Range {start}-{end}: No transactions")
            except Exception as e:
                print(f"   ❌ Range {start}-{end}: Error - {e}")
    
    # Step 3: Analysis
    print(f"\n📋 TRANSACTION ANALYSIS")
    print("=" * 30)
    
    if not all_transactions:
        print("❌ No transactions found")
        print("💡 Try expanding search range or different RPC endpoint")
        return
    
    # Sort by block number (newest first)
    all_transactions.sort(key=lambda x: x["block"], reverse=True)
    
    # Analyze transactions
    total_sent = 0.0
    bridge_count = 0
    total_gas_cost = 0.0
    
    print(f"Found {len(all_transactions)} transactions:")
    
    for i, tx in enumerate(all_transactions, 1):
        total_sent += tx["value"]
        total_gas_cost += (tx["gas_price"] * 21000) / 1e9  # Rough gas cost
        
        if "BRIDGE" in tx["type"]:
            bridge_count += 1
        
        print(f"  {i}. {tx['hash'][:10]}... | {tx['value']:.6f} ETH | {tx['type']}")
        print(f"     Block: {tx['block']} | Gas: {tx['gas_price']:.2f} gwei")
        print(f"     Explorer: https://basescan.org/tx/{tx['hash']}")
        print()
    
    # Step 4: Missing funds analysis
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
    
    # Step 5: Bridge analysis
    if bridge_count > 0:
        print(f"\n🌉 BRIDGE ANALYSIS")
        print("=" * 20)
        
        bridge_txs = [tx for tx in all_transactions if "BRIDGE" in tx["type"]]
        bridge_total = sum(tx["value"] for tx in bridge_txs)
        
        print(f"Bridge transactions: {bridge_count}")
        print(f"Total bridged: {bridge_total:.6f} ETH")
        
        for tx in bridge_txs:
            print(f"  {tx['hash'][:10]}... | {tx['value']:.6f} ETH | {tx['type']}")
        
        # Check if bridge amounts explain missing funds
        if abs(bridge_total - missing) < 0.001:
            print(f"\n✅ Bridge amounts match missing funds!")
            print(f"🔍 Funds likely stuck in bridge contracts")
            print(f"💡 Action: Check bridge contract status")
        else:
            print(f"\n⚠️  Bridge total ({bridge_total:.6f}) ≠ missing ({missing:.6f})")
            print(f"🔍 Additional investigation needed")
    
    # Step 6: Recommendations
    print(f"\n🎯 RECOMMENDATIONS")
    print("=" * 20)
    
    if bridge_count > 0:
        print("1. 🔴 URGENT: Check bridge contracts for stuck funds")
        print("2. 🟡 Monitor StarkNet address for received funds")
        print("3. 🟢 Use remaining funds for partial activation")
    else:
        print("1. 🟡 Funds likely consumed by gas fees")
        print("2. 🟢 Add more funds to continue operations")
    
    scan_time = time.time() - start_time
    print(f"\n⚡ Hyper scan completed in {scan_time:.2f} seconds")
    
    # Save results
    report = {
        "timestamp": datetime.now().isoformat(),
        "scan_time_seconds": scan_time,
        "current_balance": balance,
        "nonce": nonce,
        "transactions_found": len(all_transactions),
        "total_sent": total_sent,
        "gas_costs": total_gas_cost,
        "missing_funds": missing,
        "bridge_count": bridge_count,
        "transactions": all_transactions
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/reports/hyper_scan_{timestamp}.json"
    
    report_path = Path(output_file)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    
    print(f"\n📄 Report saved to: {output_file}")
    
    return report

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test RPC speed
        print("🚀 Testing RPC speed...")
        start = time.time()
        
        for i in range(5):
            block = get_current_block()
            print(f"   Call {i+1}: Block {block}")
        
        print(f"✅ 5 calls in {time.time() - start:.2f} seconds")
        return
    
    hyper_fast_scan()

if __name__ == "__main__":
    main()
