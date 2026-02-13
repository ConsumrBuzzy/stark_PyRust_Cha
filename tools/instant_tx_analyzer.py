#!/usr/bin/env python3
"""
PyPro Systems - Instant Transaction Analyzer
Zero-delay transaction analysis using cached data and direct RPC
"""

import requests
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Ultra-fast endpoints (prioritized by speed)
FAST_ENDPOINTS = [
    "https://base.gateway.tenderly.co",  # Fastest
    "https://mainnet.base.org",           # Official
    "https://rpc.ankr.com/base"          # Backup
]

# Known addresses
PHANTOM_ADDRESS = "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"
STARKNET_MAIN = "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"

# Bridge contracts
STARGATE_BRIDGE = "0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419"
ORBITER_BRIDGE = "0xe530d28960d48708CcF3e62Aa7B42A80bC427Aef"

class InstantAnalyzer:
    """Ultra-fast transaction analyzer with caching"""
    
    def __init__(self):
        self.cache = {}
        self.session = requests.Session()
        self.session.timeout = 3  # 3 second timeout
        
    def make_rpc_call(self, endpoint: str, method: str, params: List = None) -> Dict[str, Any]:
        """Make fast RPC call with fallback"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
            "id": 1
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=3)
            data = response.json()
            
            if "error" in data:
                return {"error": data["error"]}
            return {"result": data["result"]}
            
        except Exception:
            return {"error": f"Failed to call {endpoint}"}
    
    def get_balance_fast(self, address: str) -> float:
        """Get balance instantly"""
        cache_key = f"balance_{address}"
        
        if cache_key in self.cache:
            cached_time = self.cache[cache_key]["timestamp"]
            if time.time() - cached_time < 30:  # 30 second cache
                return self.cache[cache_key]["balance"]
        
        for endpoint in FAST_ENDPOINTS:
            result = self.make_rpc_call(endpoint, "eth_getBalance", [address, "latest"])
            if "error" not in result:
                balance = int(result["result"], 16) / 1e18
                self.cache[cache_key] = {
                    "balance": balance,
                    "timestamp": time.time()
                }
                return balance
        
        return 0.0
    
    def get_nonce_fast(self, address: str) -> int:
        """Get transaction count instantly"""
        for endpoint in FAST_ENDPOINTS:
            result = self.make_rpc_call(endpoint, "eth_getTransactionCount", [address, "latest"])
            if "error" not in result:
                return int(result["result"], 16)
        return 0
    
    def find_transactions_by_nonce(self, address: str, target_nonce: int) -> List[Dict[str, Any]]:
        """Find transactions by targeting specific nonce ranges"""
        transactions = []
        
        # Get current block
        for endpoint in FAST_ENDPOINTS:
            result = self.make_rpc_call(endpoint, "eth_blockNumber")
            if "error" not in result:
                current_block = int(result["result"], 16)
                break
        else:
            return transactions
        
        # Smart search: check blocks where transactions likely occurred
        # Recent transactions are in recent blocks
        search_blocks = min(500, current_block)
        block_step = 5  # Check every 5th block for speed
        
        print(f"🔍 Smart search: last {search_blocks} blocks (step={block_step})")
        
        for block_offset in range(0, search_blocks, block_step):
            block_num = current_block - block_offset
            
            for endpoint in FAST_ENDPOINTS:
                result = self.make_rpc_call(endpoint, "eth_getBlockByNumber", [hex(block_num), True])
                
                if "error" not in result and result["result"]:
                    block = result["result"]
                    
                    for tx in block.get("transactions", []):
                        if tx["from"].lower() == address.lower():
                            # Parse transaction quickly
                            value = int(tx["value"], 16) / 1e18
                            if value > 0:  # Only value transactions
                                tx_type = self.identify_tx_type(tx.get("to", ""))
                                
                                transactions.append({
                                    "hash": tx["hash"],
                                    "from": tx["from"],
                                    "to": tx.get("to", ""),
                                    "value": value,
                                    "block": block_num,
                                    "type": tx_type,
                                    "gas_price": int(tx.get("gasPrice", "0x0"), 16) / 1e9
                                })
                                
                                # Stop if we found enough transactions
                                if len(transactions) >= target_nonce:
                                    return transactions
                    break  # Found block, move to next
        
        return transactions
    
    def identify_tx_type(self, to_address: str) -> str:
        """Identify transaction type instantly"""
        if not to_address:
            return "CONTRACT_DEPLOY"
        
        to_lower = to_address.lower()
        if to_lower == STARGATE_BRIDGE.lower():
            return "STARKGATE_BRIDGE"
        elif to_lower == ORBITER_BRIDGE.lower():
            return "ORBITER_BRIDGE"
        elif to_lower.startswith("0x"):
            return "CONTRACT_CALL"
        else:
            return "TRANSFER"
    
    def analyze_missing_funds_instant(self) -> Dict[str, Any]:
        """Instant missing funds analysis"""
        print("⚡ INSTANT MISSING FUNDS ANALYZER")
        print("=" * 40)
        
        start_time = time.time()
        
        # Step 1: Get current state instantly
        print("📊 Step 1: Current wallet state...")
        balance = self.get_balance_fast(PHANTOM_ADDRESS)
        nonce = self.get_nonce_fast(PHANTOM_ADDRESS)
        
        print(f"   Balance: {balance:.6f} ETH")
        print(f"   Nonce: {nonce} transactions")
        
        # Step 2: Find transactions instantly
        print(f"\n🔍 Step 2: Finding {nonce} transactions...")
        transactions = self.find_transactions_by_nonce(PHANTOM_ADDRESS, nonce)
        
        print(f"   Found: {len(transactions)} transactions")
        
        # Step 3: Analyze transactions
        print(f"\n📋 Step 3: Transaction analysis...")
        
        total_sent = 0.0
        bridge_count = 0
        gas_estimate = 0.0
        
        for i, tx in enumerate(transactions, 1):
            total_sent += tx["value"]
            gas_estimate += 0.0005  # Rough gas estimate per tx
            
            if "BRIDGE" in tx["type"]:
                bridge_count += 1
            
            print(f"   {i}. {tx['hash'][:10]}... | {tx['value']:.6f} ETH | {tx['type']}")
        
        # Step 4: Missing funds calculation
        print(f"\n💰 Step 4: Missing funds calculation...")
        
        expected_initial = 0.018  # Your original expectation
        current_balance = balance
        total_outflow = total_sent + gas_estimate
        
        accounted_for = current_balance + total_outflow
        missing = expected_initial - accounted_for
        
        print(f"   Expected: {expected_initial:.6f} ETH")
        print(f"   Current: {current_balance:.6f} ETH")
        print(f"   Outflow: {total_outflow:.6f} ETH")
        print(f"   Accounted: {accounted_for:.6f} ETH")
        print(f"   Missing: {missing:.6f} ETH")
        
        # Step 5: Bridge analysis
        if bridge_count > 0:
            print(f"\n🌉 Bridge Analysis:")
            print(f"   Bridge transactions: {bridge_count}")
            print(f"   Bridge amounts: {[tx['value'] for tx in transactions if 'BRIDGE' in tx['type']]}")
            
            # Check if bridge amounts match missing funds
            bridge_total = sum(tx['value'] for tx in transactions if 'BRIDGE' in tx['type'])
            if abs(bridge_total - missing) < 0.001:
                print(f"   ✅ Bridge amounts match missing funds!")
                print(f"   🔍 Funds likely stuck in bridge contract")
            else:
                print(f"   ⚠️  Bridge total ({bridge_total:.6f}) ≠ missing ({missing:.6f})")
        
        # Step 6: Recommendations
        print(f"\n🎯 INSTANT RECOMMENDATIONS:")
        
        if missing > 0.01:
            print(f"   1. HIGH PRIORITY: Check bridge contracts for stuck funds")
            print(f"   2. MEDIUM: Use remaining {balance:.6f} ETH for partial activation")
            print(f"   3. LOW: Add {missing:.6f} ETH to complete recovery")
        elif bridge_count > 0:
            print(f"   1. Monitor bridge transactions for completion")
            print(f"   2. Check StarkNet address for received funds")
        else:
            print(f"   1. Funds consumed by gas fees")
            print(f"   2. Consider adding more funds")
        
        analysis_time = time.time() - start_time
        print(f"\n⚡ Analysis completed in {analysis_time:.2f} seconds")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "analysis_time_seconds": analysis_time,
            "current_balance": balance,
            "transaction_count": nonce,
            "found_transactions": len(transactions),
            "total_sent": total_sent,
            "bridge_count": bridge_count,
            "missing_funds": missing,
            "transactions": transactions,
            "recommendations": "Check bridge contracts" if bridge_count > 0 else "Add funds"
        }

def main():
    analyzer = InstantAnalyzer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "cache":
        # Test cache performance
        print("🚀 Testing cache performance...")
        start = time.time()
        
        for i in range(10):
            balance = analyzer.get_balance_fast(PHANTOM_ADDRESS)
        
        print(f"✅ 10 balance calls in {time.time() - start:.2f} seconds")
        return
    
    # Run instant analysis
    result = analyzer.analyze_missing_funds_instant()
    
    # Save result
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/reports/instant_analysis_{timestamp}.json"
    
    report_path = Path(output_file)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2))
    
    print(f"\n📄 Report saved to: {output_file}")

if __name__ == "__main__":
    main()
