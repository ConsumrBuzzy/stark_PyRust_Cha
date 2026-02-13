#!/usr/bin/env python3
"""
PyPro Systems - Fast Transaction Scanner
Direct transaction ID retrieval and specific analysis
"""

import requests
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Multiple API endpoints for speed
ENDPOINTS = [
    "https://api.basescan.org/api",
    "https://base.gateway.tenderly.co",
    "https://mainnet.base.org"
]

# Known addresses
PHANTOM_ADDRESS = "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"
STARKNET_MAIN = "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
STARKNET_GHOST = "0x000000000000000000000000ff01e0776369ce51debb16dfb70f23c16d875463"

# Bridge contracts
STARGATE_BRIDGE = "0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419"
ORBITER_BRIDGE = "0xe530d28960d48708CcF3e62Aa7B42A80bC427Aef"
RHINO_CONTRACT = "0x0000000000a39bb9e7400b6e9b0c6a1d40a7c5b0"

def get_transaction_ids_fast(address: str, limit: int = 50) -> List[str]:
    """Get transaction IDs using BaseScan API (fastest method)"""
    try:
        # Method 1: BaseScan API
        url = "https://api.basescan.org/api"
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "desc",
            "limit": limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data["status"] == "1":
            return [tx["hash"] for tx in data["result"]]
        else:
            print(f"⚠️  BaseScan API error: {data.get('result', 'Unknown')}")
            
    except Exception as e:
        print(f"⚠️  BaseScan failed: {e}")
    
    # Fallback: Use web3 RPC with block range optimization
    return get_transaction_ids_rpc(address, limit)

def get_transaction_ids_rpc(address: str, limit: int = 50) -> List[str]:
    """Get transaction IDs using RPC with optimized search"""
    try:
        # Get current nonce to know how many transactions to look for
        rpc_url = "https://mainnet.base.org"
        
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionCount",
            "params": [address, "latest"],
            "id": 1
        }
        
        response = requests.post(rpc_url, json=payload, timeout=5)
        data = response.json()
        
        if "error" in data:
            print(f"❌ RPC error: {data['error']}")
            return []
        
        nonce = int(data["result"], 16)
        if nonce == 0:
            print("📝 No transactions found")
            return []
        
        print(f"🔍 Found {nonce} transactions, scanning last {min(nonce, limit)}...")
        
        # Get recent block number
        payload = {
            "jsonrpc": "2.0", 
            "method": "eth_blockNumber",
            "params": [],
            "id": 2
        }
        
        response = requests.post(rpc_url, json=payload, timeout=5)
        current_block = int(response.json()["result"], 16)
        
        # Search recent blocks more efficiently
        transactions = []
        blocks_to_check = min(1000, current_block)  # Check last 1000 blocks max
        
        for block_offset in range(0, blocks_to_check, 10):  # Check every 10th block
            block_num = current_block - block_offset
            
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBlockByNumber", 
                "params": [hex(block_num), True],
                "id": 3
            }
            
            try:
                response = requests.post(rpc_url, json=payload, timeout=3)
                block_data = response.json()
                
                if "result" in block_data and block_data["result"]["transactions"]:
                    for tx in block_data["result"]["transactions"]:
                        if tx["from"].lower() == address.lower() and tx["hash"] not in transactions:
                            transactions.append(tx["hash"])
                            if len(transactions) >= limit:
                                return transactions[:limit]
                                
            except Exception:
                continue
        
        return transactions
        
    except Exception as e:
        print(f"❌ RPC method failed: {e}")
        return []

def analyze_transaction_fast(tx_hash: str) -> Dict[str, Any]:
    """Analyze a specific transaction quickly"""
    try:
        # Use BaseScan API for transaction details
        url = "https://api.basescan.org/api"
        params = {
            "module": "proxy",
            "action": "eth_getTransactionByHash",
            "txhash": tx_hash
        }
        
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if data["status"] != "1":
            return {"success": False, "error": "Transaction not found"}
        
        tx_data = data["result"]
        
        # Get receipt
        params["action"] = "eth_getTransactionReceipt"
        response = requests.get(url, params=params, timeout=5)
        receipt_data = response.json()
        
        if receipt_data["status"] == "1":
            receipt = receipt_data["result"]
            status = receipt["status"] == "0x1"
            gas_used = int(receipt["gasUsed"], 16)
            block_number = int(receipt["blockNumber"], 16)
        else:
            status = False
            gas_used = 0
            block_number = 0
        
        # Parse transaction details
        from_addr = tx_data["from"]
        to_addr = tx_data.get("to", "")
        value = int(tx_data["value"], 16) / 1e18
        gas_price = int(tx_data["gasPrice"], 16) / 1e9
        
        # Identify transaction type
        tx_type = "UNKNOWN"
        if to_addr:
            to_lower = to_addr.lower()
            if to_lower == STARGATE_BRIDGE.lower():
                tx_type = "STARKGATE_BRIDGE"
            elif to_lower == ORBITER_BRIDGE.lower():
                tx_type = "ORBITER_BRIDGE"
            elif to_lower == RHINO_CONTRACT.lower():
                tx_type = "RHINO_BRIDGE"
            elif to_lower.startswith("0x"):
                tx_type = "CONTRACT_INTERACTION"
            else:
                tx_type = "TRANSFER"
        
        return {
            "success": True,
            "hash": tx_hash,
            "from": from_addr,
            "to": to_addr,
            "value_eth": value,
            "gas_price_gwei": gas_price,
            "gas_used": gas_used,
            "gas_cost_eth": (gas_used * gas_price) / 1e9,
            "status": "SUCCESS" if status else "FAILED",
            "block_number": block_number,
            "type": tx_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "hash": tx_hash}

def scan_phantom_transactions():
    """Fast scan of Phantom wallet transactions"""
    print("🚀 FAST PHANTOM TRANSACTION SCANNER")
    print("=" * 50)
    
    # Step 1: Get transaction IDs fast
    print("📡 Step 1: Retrieving transaction IDs...")
    tx_ids = get_transaction_ids_fast(PHANTOM_ADDRESS, limit=20)
    
    if not tx_ids:
        print("❌ No transactions found")
        return
    
    print(f"✅ Found {len(tx_ids)} transaction IDs")
    
    # Step 2: Analyze transactions in parallel
    print("\n⚡ Step 2: Analyzing transactions (parallel)...")
    
    all_transactions = []
    bridge_transactions = []
    total_value_sent = 0.0
    total_gas_spent = 0.0
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all transaction analyses
        future_to_tx = {
            executor.submit(analyze_transaction_fast, tx_id): tx_id 
            for tx_id in tx_ids
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_tx):
            tx_id = future_to_tx[future]
            try:
                result = future.result(timeout=10)
                if result["success"]:
                    all_transactions.append(result)
                    total_value_sent += result["value_eth"]
                    total_gas_spent += result["gas_cost_eth"]
                    
                    # Check if it's a bridge transaction
                    if "BRIDGE" in result["type"]:
                        bridge_transactions.append(result)
                    
                    # Display progress
                    status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
                    print(f"  {status_icon} {result['hash'][:10]}... | "
                          f"{result['value_eth']:.6f} ETH | {result['type']}")
                else:
                    print(f"  ❌ {tx_id[:10]}... | ERROR: {result.get('error', 'Unknown')}")
                    
            except Exception as e:
                print(f"  ❌ {tx_id[:10]}... | TIMEOUT: {e}")
    
    # Step 3: Summary analysis
    print(f"\n📊 STEP 3: TRANSACTION ANALYSIS")
    print("=" * 50)
    
    print(f"📈 SUMMARY:")
    print(f"   Total Transactions: {len(all_transactions)}")
    print(f"   Bridge Transactions: {len(bridge_transactions)}")
    print(f"   Total Value Sent: {total_value_sent:.6f} ETH (${total_value_sent * 3500:.2f})")
    print(f"   Total Gas Spent: {total_gas_spent:.6f} ETH (${total_gas_spent * 3500:.2f})")
    print(f"   Net Cost: {(total_value_sent + total_gas_spent):.6f} ETH")
    
    # Bridge analysis
    if bridge_transactions:
        print(f"\n🌉 BRIDGE TRANSACTIONS:")
        for i, tx in enumerate(bridge_transactions, 1):
            print(f"   {i}. {tx['hash']}")
            print(f"      Type: {tx['type']}")
            print(f"      Amount: {tx['value_eth']:.6f} ETH")
            print(f"      Status: {tx['status']}")
            print(f"      Gas Cost: {tx['gas_cost_eth']:.6f} ETH")
            print(f"      Explorer: https://basescan.org/tx/{tx['hash']}")
            print()
    
    # Missing funds analysis
    initial_expected = 0.018  # From your original expectation
    current_balance = 0.005715  # Current Phantom balance
    total_outflow = total_value_sent + total_gas_spent
    
    print(f"💰 FUNDS ANALYSIS:")
    print(f"   Expected (initial): {initial_expected:.6f} ETH")
    print(f"   Current balance: {current_balance:.6f} ETH")
    print(f"   Total outflow: {total_outflow:.6f} ETH")
    print(f"   Accounted for: {current_balance + total_outflow:.6f} ETH")
    
    missing = initial_expected - (current_balance + total_outflow)
    if missing > 0:
        print(f"   ❌ Still missing: {missing:.6f} ETH (${missing * 3500:.2f})")
    else:
        print(f"   ✅ All funds accounted for!")
    
    # Save detailed report
    report = {
        "timestamp": datetime.now().isoformat(),
        "phantom_address": PHANTOM_ADDRESS,
        "total_transactions": len(all_transactions),
        "bridge_transactions": len(bridge_transactions),
        "total_value_sent": total_value_sent,
        "total_gas_spent": total_gas_spent,
        "current_balance": current_balance,
        "missing_funds": max(0, missing),
        "transactions": all_transactions,
        "bridge_txs": bridge_transactions
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/reports/fast_tx_scan_{timestamp}.json"
    
    report_path = Path(output_file)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    
    print(f"\n📄 Detailed report saved to: {output_file}")
    
    return report

def main():
    if len(sys.argv) > 1:
        # Analyze specific transaction hash
        tx_hash = sys.argv[1]
        print(f"🔍 Analyzing specific transaction: {tx_hash}")
        print("=" * 50)
        
        result = analyze_transaction_fast(tx_hash)
        if result["success"]:
            print(f"✅ Transaction Found:")
            print(f"   Hash: {result['hash']}")
            print(f"   Type: {result['type']}")
            print(f"   Value: {result['value_eth']:.6f} ETH")
            print(f"   Status: {result['status']}")
            print(f"   Gas Cost: {result['gas_cost_eth']:.6f} ETH")
            print(f"   Explorer: https://basescan.org/tx/{result['hash']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown')}")
    else:
        # Scan all Phantom transactions
        scan_phantom_transactions()

if __name__ == "__main__":
    main()
