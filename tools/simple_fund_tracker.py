#!/usr/bin/env python3
"""
PyPro Systems - Simple Fund Tracker
Track funds using direct web requests without complex API clients
"""

import requests
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

def get_balance_base(address: str) -> Dict[str, Any]:
    """Get balance for Base network address using direct API call"""
    try:
        # Use BaseScan API with proper parameters
        url = "https://api.basescan.org/api"
        params = {
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest"
        }
        
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        if data["status"] == "1":
            balance_wei = int(data["result"])
            balance_eth = balance_wei / 1e18
            return {
                "success": True,
                "balance_eth": balance_eth,
                "balance_usd": balance_eth * 3500,  # Approximate ETH price
                "address": address
            }
        else:
            return {
                "success": False,
                "error": data.get("result", "Unknown API error"),
                "address": address
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "address": address
        }

def get_transactions_base(address: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent transactions for Base network address"""
    try:
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
        
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        if data["status"] == "1":
            transactions = []
            for tx in data["result"][:limit]:
                transactions.append({
                    "hash": tx["hash"],
                    "timestamp": datetime.fromtimestamp(int(tx["timeStamp"])).isoformat(),
                    "value_eth": float(tx["value"]) / 1e18,
                    "from_address": tx["from"],
                    "to_address": tx["to"],
                    "status": "success" if tx["isError"] == "0" else "failed",
                    "confirmations": int(tx["confirmations"])
                })
            return transactions
        else:
            return []
            
    except Exception as e:
        print(f"Error getting transactions: {e}")
        return []

def analyze_missing_funds(expected_amount: float, addresses: List[str]) -> Dict[str, Any]:
    """Analyze missing funds across multiple addresses"""
    print(f"🔍 Analyzing {expected_amount:.6f} ETH across {len(addresses)} addresses")
    print("=" * 60)
    
    total_found = 0.0
    total_usd = 0.0
    address_results = []
    
    for address in addresses:
        print(f"📍 Checking {address[:10]}...{address[-8:]}")
        
        # Get balance
        balance_result = get_balance_base(address)
        
        if balance_result["success"]:
            balance_eth = balance_result["balance_eth"]
            balance_usd = balance_result["balance_usd"]
            total_found += balance_eth
            total_usd += balance_usd
            
            status = "✅" if balance_eth > 0 else "🔍"
            print(f"  {status} Balance: {balance_eth:.6f} ETH (${balance_usd:.2f})")
            
            # Get recent transactions
            txs = get_transactions_base(address, limit=3)
            if txs:
                print(f"  📜 Recent transactions:")
                for tx in txs:
                    direction = "OUT" if tx["from_address"].lower() == address.lower() else "IN"
                    status_icon = "✅" if tx["status"] == "success" else "❌"
                    print(f"    {status_icon} {direction} {tx['value_eth']:.6f} ETH - {tx['timestamp']}")
            
            address_results.append({
                "address": address,
                "balance_eth": balance_eth,
                "balance_usd": balance_usd,
                "success": True,
                "transactions": txs
            })
        else:
            print(f"  ❌ Error: {balance_result['error']}")
            address_results.append({
                "address": address,
                "balance_eth": 0.0,
                "balance_usd": 0.0,
                "success": False,
                "error": balance_result["error"]
            })
        
        print()
    
    # Calculate missing amount
    missing_eth = max(0, expected_amount - total_found)
    missing_usd = missing_eth * 3500
    
    print("=" * 60)
    print(f"💰 Expected: {expected_amount:.6f} ETH (${expected_amount * 3500:.2f})")
    print(f"💰 Found: {total_found:.6f} ETH (${total_usd:.2f})")
    print(f"❌ Missing: {missing_eth:.6f} ETH (${missing_usd:.2f})")
    
    # Generate recommendations
    recommendations = []
    if missing_eth > 0:
        recommendations.append(f"Missing {missing_eth:.6f} ETH (${missing_usd:.2f})")
        
        # Check for recent outflows
        for result in address_results:
            if result["success"] and result["transactions"]:
                for tx in result["transactions"]:
                    if (tx["from_address"].lower() == result["address"].lower() and 
                        tx["status"] == "success" and tx["value_eth"] > 0):
                        recommendations.append(
                            f"Recent outflow: {tx['value_eth']:.6f} ETH from {result['address'][:10]}... "
                            f"on {tx['timestamp'][:10]}"
                        )
    else:
        recommendations.append("All expected funds accounted for")
    
    print("\n📋 Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    return {
        "expected_amount_eth": expected_amount,
        "expected_amount_usd": expected_amount * 3500,
        "total_found_eth": total_found,
        "total_found_usd": total_usd,
        "missing_eth": missing_eth,
        "missing_usd": missing_usd,
        "address_results": address_results,
        "recommendations": recommendations,
        "timestamp": datetime.now().isoformat()
    }

def generate_report(analysis: Dict[str, Any], output_file: str = None):
    """Generate detailed report"""
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/reports/fund_analysis_{timestamp}.md"
    
    report = f"""# Fund Analysis Report

**Generated**: {analysis['timestamp']}  
**Expected Amount**: {analysis['expected_amount_eth']:.6f} ETH (${analysis['expected_amount_usd']:.2f})  
**Total Found**: {analysis['total_found_eth']:.6f} ETH (${analysis['total_found_usd']:.2f})  
**Missing**: {analysis['missing_eth']:.6f} ETH (${analysis['missing_usd']:.2f})

## Address Breakdown

"""
    
    for result in analysis["address_results"]:
        addr = result["address"]
        if result["success"]:
            report += f"### {addr[:10]}...{addr[-8:]}\n"
            report += f"- **Balance**: {result['balance_eth']:.6f} ETH (${result['balance_usd']:.2f})\n"
            report += f"- **Status**: {'✅ Funded' if result['balance_eth'] > 0 else '🔍 Empty'}\n"
            
            if result["transactions"]:
                report += "- **Recent Transactions**:\n"
                for tx in result["transactions"]:
                    direction = "OUT" if tx["from_address"].lower() == addr.lower() else "IN"
                    report += f"  - {direction} {tx['value_eth']:.6f} ETH ({tx['status']}) - {tx['timestamp']}\n"
            report += "\n"
        else:
            report += f"### {addr[:10]}...{addr[-8:]}\n"
            report += f"- **Error**: {result['error']}\n\n"
    
    report += "## Recommendations\n\n"
    for i, rec in enumerate(analysis["recommendations"], 1):
        report += f"{i}. {rec}\n"
    
    # Save report
    report_path = Path(output_file)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    
    print(f"\n📄 Report saved to: {output_file}")
    return output_file

def main():
    if len(sys.argv) < 3:
        print("Usage: python simple_fund_tracker.py <expected_amount_eth> <addresses_comma_separated> [output_file]")
        print("Example: python simple_fund_tracker.py 0.018 \"0x1234...,0x5678...\" report.md")
        return
    
    try:
        expected_amount = float(sys.argv[1])
        addresses_input = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        
        # Parse addresses
        if "," in addresses_input:
            addresses = [addr.strip() for addr in addresses_input.split(",")]
        else:
            addresses = [addresses_input.strip()]
        
        # Validate addresses
        valid_addresses = []
        for addr in addresses:
            addr = addr.strip()
            if addr.startswith("0x") and (len(addr) == 42 or len(addr) == 66):
                valid_addresses.append(addr)
            else:
                print(f"⚠️  Invalid address format: {addr}")
        
        if not valid_addresses:
            print("❌ No valid addresses provided")
            return
        
        # Run analysis
        analysis = analyze_missing_funds(expected_amount, valid_addresses)
        
        # Generate report
        if output_file:
            generate_report(analysis, output_file)
        
    except ValueError:
        print("❌ Invalid amount. Please provide a number in ETH.")
    except KeyboardInterrupt:
        print("\n⚠️  Analysis cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
