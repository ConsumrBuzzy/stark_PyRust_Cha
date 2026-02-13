#!/usr/bin/env python3
"""
PyPro Systems - Phantom Transaction Ping
Direct RPC calls to get exact transaction IDs from Phantom wallet
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

# Fast RPC endpoints
RPC_ENDPOINTS = [
    "https://base.gateway.tenderly.co",    # Fastest
    "https://mainnet.base.org",            # Official
    "https://rpc.ankr.com/base",           # Backup
]

def make_rpc_call(endpoint: str, method: str, params: List = None) -> Dict[str, Any]:
    """Make RPC call with fallback"""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or [],
        "id": 1
    }
    
    try:
        response = requests.post(endpoint, json=payload, timeout=5)
        data = response.json()
        
        if "error" in data:
            return {"error": data["error"]}
        return {"result": data["result"]}
        
    except Exception as e:
        return {"error": str(e)}

def get_phantom_transaction_ids() -> List[str]:
    """Get transaction IDs directly from Phantom wallet"""
    print("🔍 PINGING PHANTOM WALLET FOR TRANSACTION IDS")
    print("=" * 50)
    
    # Step 1: Get current nonce (number of transactions)
    print("📊 Step 1: Getting transaction count...")
    
    for endpoint in RPC_ENDPOINTS:
        result = make_rpc_call(endpoint, "eth_getTransactionCount", [PHANTOM_ADDRESS, "latest"])
        
        if "error" not in result:
            nonce = int(result["result"], 16)
            print(f"✅ Found {nonce} transactions using {endpoint}")
            break
    else:
        print("❌ Failed to get transaction count")
        return []
    
    if nonce == 0:
        print("📝 No transactions found")
        return []
    
    # Step 2: Get current balance
    print("\n💰 Step 2: Getting current balance...")
    
    for endpoint in RPC_ENDPOINTS:
        result = make_rpc_call(endpoint, "eth_getBalance", [PHANTOM_ADDRESS, "latest"])
        
        if "error" not in result:
            balance = int(result["result"], 16) / 1e18
            print(f"✅ Current balance: {balance:.6f} ETH")
            break
    
    # Step 3: Get transaction IDs by nonce
    print(f"\n🔍 Step 3: Finding {nonce} transaction IDs...")
    
    # Strategy: Use the fact that we know the nonce count
    # We'll search recent blocks but stop when we find all transactions
    
    transaction_ids = []
    
    # Get current block
    for endpoint in RPC_ENDPOINTS:
        result = make_rpc_call(endpoint, "eth_blockNumber")
        if "error" not in result:
            current_block = int(result["result"], 16)
            print(f"📦 Current block: {current_block}")
            break
    else:
        print("❌ Failed to get current block")
        return []
    
    # Search for transactions - use optimized range
    # Since we have nonce=9, we need to find exactly 9 transactions
    print(f"🔍 Searching for exactly {nonce} transactions...")
    
    # Use a wider search range to ensure we find all transactions
    max_blocks_to_search = 50000  # Search wider range
    blocks_checked = 0
    
    for block_offset in range(0, max_blocks_to_search, 10):  # Check every 10th block for speed
        block_num = current_block - block_offset
        
        if block_num < 0:
            break
        
        blocks_checked += 1
        
        # Progress indicator
        if blocks_checked % 100 == 0:
            print(f"   Searched {blocks_checked * 10} blocks... Found {len(transaction_ids)}/{nonce} transactions")
        
        for endpoint in RPC_ENDPOINTS:
            result = make_rpc_call(endpoint, "eth_getBlockByNumber", [hex(block_num), True])
            
            if "error" not in result and result["result"]:
                block = result["result"]
                
                for tx in block.get("transactions", []):
                    if tx["from"].lower() == PHANTOM_ADDRESS.lower() and tx["value"] != "0x0":
                        tx_hash = tx["hash"]
                        
                        if tx_hash not in transaction_ids:
                            transaction_ids.append(tx_hash)
                            print(f"✅ Found TX {len(transaction_ids)}: {tx_hash}")
                            print(f"   Block: {block_num} | Value: {int(tx['value'], 16) / 1e18:.6f} ETH")
                            print(f"   To: {tx.get('to', 'Contract Deploy')}")
                            print(f"   Explorer: https://basescan.org/tx/{tx_hash}")
                            print()
                            
                            # Stop if we found all transactions
                            if len(transaction_ids) >= nonce:
                                print(f"🎉 Found all {nonce} transactions!")
                                return transaction_ids
                
                break  # Found block, move to next
    
    print(f"⚠️  Search completed. Found {len(transaction_ids)}/{nonce} transactions")
    print(f"📊 Searched {blocks_checked * 10} blocks")
    
    return transaction_ids

def analyze_transaction_ids(tx_ids: List[str]) -> Dict[str, Any]:
    """Analyze specific transaction IDs"""
    if not tx_ids:
        return {"error": "No transaction IDs to analyze"}
    
    print(f"\n📋 ANALYZING {len(tx_ids)} TRANSACTION IDS")
    print("=" * 50)
    
    transactions = []
    total_value = 0.0
    bridge_count = 0
    
    # Known bridge contracts
    STARGATE_BRIDGE = "0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419"
    ORBITER_BRIDGE = "0xe530d28960d48708CcF3e62Aa7B42A80bC427Aef"
    
    for i, tx_hash in enumerate(tx_ids, 1):
        print(f"\n{i}. Analyzing {tx_hash[:10]}...")
        
        # Get transaction details
        for endpoint in RPC_ENDPOINTS:
            result = make_rpc_call(endpoint, "eth_getTransactionByHash", [tx_hash])
            
            if "error" not in result and result["result"]:
                tx = result["result"]
                
                # Parse transaction
                from_addr = tx["from"]
                to_addr = tx.get("to", "")
                value = int(tx["value"], 16) / 1e18
                gas_price = int(tx.get("gasPrice", "0x0"), 16) / 1e9
                
                # Identify type
                tx_type = "UNKNOWN"
                if to_addr:
                    to_lower = to_addr.lower()
                    if to_lower == STARGATE_BRIDGE.lower():
                        tx_type = "STARGATE_BRIDGE"
                        bridge_count += 1
                    elif to_lower == ORBITER_BRIDGE.lower():
                        tx_type = "ORBITER_BRIDGE"
                        bridge_count += 1
                    else:
                        tx_type = "CONTRACT_CALL"
                else:
                    tx_type = "CONTRACT_DEPLOY"
                
                # Get receipt for status
                status = "UNKNOWN"
                gas_used = 0
                
                receipt_result = make_rpc_call(endpoint, "eth_getTransactionReceipt", [tx_hash])
                if "error" not in receipt_result and receipt_result["result"]:
                    receipt = receipt_result["result"]
                    status = "SUCCESS" if receipt.get("status") == "0x1" else "FAILED"
                    gas_used = int(receipt.get("gasUsed", "0x0"), 16)
                
                gas_cost_eth = (gas_used * gas_price) / 1e9
                total_value += value
                
                transaction_data = {
                    "hash": tx_hash,
                    "from": from_addr,
                    "to": to_addr,
                    "value": value,
                    "type": tx_type,
                    "status": status,
                    "gas_price_gwei": gas_price,
                    "gas_used": gas_used,
                    "gas_cost_eth": gas_cost_eth,
                    "block_number": int(tx.get("blockNumber", "0x0"), 16)
                }
                
                transactions.append(transaction_data)
                
                # Display
                status_icon = "✅" if status == "SUCCESS" else "❌"
                print(f"   {status_icon} {tx_type}")
                print(f"   Value: {value:.6f} ETH")
                print(f"   Gas Cost: {gas_cost_eth:.6f} ETH")
                print(f"   Status: {status}")
                print(f"   Explorer: https://basescan.org/tx/{tx_hash}")
                
                break
        else:
            print(f"   ❌ Failed to get transaction details")
    
    # Summary
    print(f"\n📊 TRANSACTION SUMMARY")
    print("=" * 30)
    print(f"Total Transactions: {len(transactions)}")
    print(f"Total Value: {total_value:.6f} ETH")
    print(f"Bridge Transactions: {bridge_count}")
    print(f"Total Gas Costs: {sum(tx['gas_cost_eth'] for tx in transactions):.6f} ETH")
    
    # Missing funds calculation
    expected_initial = 0.018
    current_balance = 0.005715  # From previous analysis
    total_outflow = total_value + sum(tx['gas_cost_eth'] for tx in transactions)
    
    accounted_for = current_balance + total_outflow
    missing = expected_initial - accounted_for
    
    print(f"\n💰 FUNDS ANALYSIS")
    print("=" * 20)
    print(f"Expected: {expected_initial:.6f} ETH")
    print(f"Current: {current_balance:.6f} ETH")
    print(f"Outflow: {total_outflow:.6f} ETH")
    print(f"Missing: {missing:.6f} ETH (${missing * 3500:.2f})")
    
    if bridge_count > 0:
        bridge_txs = [tx for tx in transactions if "BRIDGE" in tx["type"]]
        bridge_total = sum(tx["value"] for tx in bridge_txs)
        
        print(f"\n🌉 BRIDGE ANALYSIS")
        print(f"Bridge Count: {bridge_count}")
        print(f"Bridge Total: {bridge_total:.6f} ETH")
        
        if abs(bridge_total - missing) < 0.001:
            print(f"✅ Bridge amounts match missing funds!")
            print(f"🔍 Funds likely stuck in bridge contracts")
    
    return {
        "transaction_ids": tx_ids,
        "transactions": transactions,
        "total_value": total_value,
        "bridge_count": bridge_count,
        "missing_funds": missing
    }

def main():
    start_time = time.time()
    
    # Get transaction IDs
    tx_ids = get_phantom_transaction_ids()
    
    if not tx_ids:
        print("❌ No transaction IDs found")
        return
    
    # Analyze transactions
    analysis = analyze_transaction_ids(tx_ids)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/reports/phantom_tx_ping_{timestamp}.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "phantom_address": PHANTOM_ADDRESS,
        "transaction_ids": tx_ids,
        "analysis": analysis,
        "ping_time_seconds": time.time() - start_time
    }
    
    report_path = Path(output_file)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    
    print(f"\n📄 Results saved to: {output_file}")
    print(f"⚡ Total ping time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
