#!/usr/bin/env python3
"""
PyPro Systems - Transaction Analyzer
Analyze transaction history for fund recovery
"""

import requests
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Base network endpoints
BASE_RPC_URL = "https://mainnet.base.org"
BASESCAN_API_URL = "https://api.basescan.org/api"

# Known bridge contracts
STARGATE_BRIDGE = "0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419"
OTHER_BRIDGES = [
    "0x4200000000000000000000000000000000000010",  # LayerZero
    "0x2d5c7e31b7a53b31c4634022c6d4130986b1f6c0",  # Hop Bridge
]

def make_rpc_call(method: str, params: List = None) -> Dict[str, Any]:
    """Make JSON-RPC call to Base network"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
            "id": 1
        }
        
        response = requests.post(BASE_RPC_URL, json=payload, timeout=30)
        data = response.json()
        
        if "error" in data:
            raise Exception(f"RPC Error: {data['error']}")
        
        return data["result"]
        
    except Exception as e:
        print(f"RPC call failed: {e}")
        raise

def get_transaction_details(tx_hash: str) -> Dict[str, Any]:
    """Get detailed transaction information"""
    try:
        tx_details = make_rpc_call("eth_getTransactionByHash", [tx_hash])
        tx_receipt = make_rpc_call("eth_getTransactionReceipt", [tx_hash])
        
        if not tx_details or not tx_receipt:
            return {"success": False, "error": "Transaction not found"}
        
        # Parse transaction details
        from_addr = tx_details.get("from", "")
        to_addr = tx_details.get("to", "")
        value = int(tx_details.get("value", "0x0"), 16) / 1e18
        gas_used = int(tx_receipt.get("gasUsed", "0x0"), 16)
        gas_price = int(tx_details.get("gasPrice", "0x0"), 16)
        
        # Calculate gas cost
        gas_cost_eth = (gas_used * gas_price) / 1e18
        
        # Check status
        status = tx_receipt.get("status", "0x0") == "0x1"
        
        return {
            "success": True,
            "hash": tx_hash,
            "from_address": from_addr,
            "to_address": to_addr,
            "value_eth": value,
            "gas_used": gas_used,
            "gas_price": gas_price,
            "gas_cost_eth": gas_cost_eth,
            "status": status,
            "block_number": int(tx_receipt.get("blockNumber", "0x0"), 16),
            "timestamp": datetime.now().isoformat()  # Would need block timestamp for accuracy
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_transaction_history(address: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get transaction history using BaseScan API"""
    try:
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "desc",
            "limit": limit
        }
        
        response = requests.get(BASESCAN_API_URL, params=params, timeout=30)
        data = response.json()
        
        if data["status"] != "1":
            return []
        
        transactions = []
        for tx in data["result"]:
            transactions.append({
                "hash": tx["hash"],
                "timestamp": datetime.fromtimestamp(int(tx["timeStamp"])).isoformat(),
                "value_eth": float(tx["value"]) / 1e18,
                "from_address": tx["from"],
                "to_address": tx["to"],
                "gas_used": int(tx["gasUsed"]),
                "gas_price": int(tx["gasPrice"]),
                "gas_cost_eth": (int(tx["gasUsed"]) * int(tx["gasPrice"])) / 1e18,
                "status": "success" if tx["isError"] == "0" else "failed",
                "confirmations": int(tx["confirmations"]),
                "block_number": int(tx["blockNumber"])
            })
        
        return transactions
        
    except Exception as e:
        print(f"Error getting transaction history: {e}")
        return []

def analyze_bridge_transactions(transactions: List[Dict[str, Any]], target_address: str) -> Dict[str, Any]:
    """Analyze transactions for bridge activity"""
    bridge_analysis = {
        "total_transactions": len(transactions),
        "bridge_transactions": [],
        "total_sent_to_bridges": 0.0,
        "total_gas_spent": 0.0,
        "potential_issues": []
    }
    
    for tx in transactions:
        # Check if transaction is to a known bridge
        to_addr = tx["to_address"].lower() if tx["to_address"] else ""
        
        is_bridge = (
            to_addr == STARGATE_BRIDGE.lower() or
            any(to_addr == bridge.lower() for bridge in OTHER_BRIDGES)
        )
        
        if is_bridge:
            bridge_analysis["bridge_transactions"].append(tx)
            bridge_analysis["total_sent_to_bridges"] += tx["value_eth"]
            
            # Check for failed bridge transactions
            if tx["status"] == "failed":
                bridge_analysis["potential_issues"].append({
                    "type": "failed_bridge",
                    "hash": tx["hash"],
                    "value": tx["value_eth"],
                    "gas_lost": tx["gas_cost_eth"]
                })
        
        # Track all gas costs
        bridge_analysis["total_gas_spent"] += tx["gas_cost_eth"]
    
    return bridge_analysis

def analyze_phantom_wallet(address: str) -> Dict[str, Any]:
    """Comprehensive analysis of Phantom wallet transactions"""
    print(f"🔍 Analyzing Phantom wallet: {address[:10]}...{address[-8:]}")
    print("=" * 60)
    
    # Get transaction history
    transactions = get_transaction_history(address, limit=20)
    
    if not transactions:
        print("❌ No transaction history found")
        return {"success": False, "error": "No transactions found"}
    
    print(f"📜 Found {len(transactions)} transactions")
    
    # Analyze bridge activity
    bridge_analysis = analyze_bridge_transactions(transactions, address)
    
    # Current balance
    try:
        balance_wei = make_rpc_call("eth_getBalance", [address, "latest"])
        current_balance = int(balance_wei, 16) / 1e18
    except:
        current_balance = 0.0
    
    print(f"\n💰 Current Balance: {current_balance:.6f} ETH")
    print(f"🌉 Bridge Transactions: {len(bridge_analysis['bridge_transactions'])}")
    print(f"💸 Total Gas Spent: {bridge_analysis['total_gas_spent']:.6f} ETH")
    
    if bridge_analysis["total_sent_to_bridges"] > 0:
        print(f"📤 Sent to Bridges: {bridge_analysis['total_sent_to_bridges']:.6f} ETH")
    
    # Detailed transaction breakdown
    print(f"\n📋 Transaction Breakdown:")
    total_value_sent = 0.0
    total_value_received = 0.0
    
    for i, tx in enumerate(transactions[:10], 1):  # Show first 10
        direction = "OUT" if tx["from_address"].lower() == address.lower() else "IN"
        status_icon = "✅" if tx["status"] == "success" else "❌"
        
        if direction == "OUT":
            total_value_sent += tx["value_eth"]
        else:
            total_value_received += tx["value_eth"]
        
        # Check if it's a bridge transaction
        is_bridge = tx["to_address"] and tx["to_address"].lower() == STARGATE_BRIDGE.lower()
        bridge_icon = "🌉" if is_bridge else ""
        
        print(f"  {i:2d}. {status_icon} {direction} {tx['value_eth']:.6f} ETH {bridge_icon}")
        print(f"      Hash: {tx['hash'][:10]}...{tx['hash'][-8:]}")
        print(f"      Time: {tx['timestamp'][:19]}")
        print(f"      Gas: {tx['gas_cost_eth']:.6f} ETH")
        
        if is_bridge:
            print(f"      🌉 STARGATE BRIDGE TRANSACTION")
        
        print()
    
    # Summary analysis
    net_flow = total_value_received - total_value_sent
    print(f"📊 Summary:")
    print(f"  Total Sent: {total_value_sent:.6f} ETH")
    print(f"  Total Received: {total_value_received:.6f} ETH")
    print(f"  Net Flow: {net_flow:+.6f} ETH")
    print(f"  Gas Costs: {bridge_analysis['total_gas_spent']:.6f} ETH")
    
    # Identify potential issues
    issues = []
    
    if bridge_analysis["potential_issues"]:
        issues.append(f"{len(bridge_analysis['potential_issues'])} failed bridge transactions")
    
    if bridge_analysis["total_sent_to_bridges"] > 0:
        issues.append(f"{bridge_analysis['total_sent_to_bridges']:.6f} ETH sent to bridges")
    
    if bridge_analysis["total_gas_spent"] > 0.01:  # High gas usage
        issues.append(f"High gas consumption: {bridge_analysis['total_gas_spent']:.6f} ETH")
    
    if issues:
        print(f"\n⚠️  Potential Issues:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    
    # Recommendations
    recommendations = []
    
    if bridge_analysis["total_sent_to_bridges"] > 0:
        recommendations.append("Check bridge contract for stuck funds")
    
    if bridge_analysis["potential_issues"]:
        recommendations.append("Investigate failed bridge transactions")
    
    if current_balance < 0.01:
        recommendations.append("Consider adding more funds for operations")
    
    if recommendations:
        print(f"\n📋 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    return {
        "success": True,
        "address": address,
        "current_balance": current_balance,
        "total_transactions": len(transactions),
        "bridge_analysis": bridge_analysis,
        "transactions": transactions,
        "total_sent": total_value_sent,
        "total_received": total_value_received,
        "net_flow": net_flow,
        "issues": issues,
        "recommendations": recommendations,
        "timestamp": datetime.now().isoformat()
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_transactions.py <address>")
        print("Example: python analyze_transactions.py 0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9")
        return
    
    address = sys.argv[1]
    
    # Validate address
    if not address.startswith("0x") or len(address) != 42:
        print("❌ Invalid address format. Expected 0x + 40 hex characters")
        return
    
    try:
        analysis = analyze_phantom_wallet(address)
        
        # Save analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/reports/transaction_analysis_{timestamp}.json"
        
        report_path = Path(output_file)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(analysis, indent=2))
        
        print(f"\n📄 Analysis saved to: {output_file}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Analysis cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
