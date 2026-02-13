#!/usr/bin/env python3
"""
PyPro Systems - Web3 Fund Tracker
Track funds using direct Web3 RPC calls
"""

import requests
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Base network RPC endpoint
BASE_RPC_URL = "https://mainnet.base.org"

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

def get_balance_web3(address: str) -> Dict[str, Any]:
    """Get balance using Web3 RPC"""
    try:
        balance_wei = make_rpc_call("eth_getBalance", [address, "latest"])
        balance_eth = int(balance_wei, 16) / 1e18
        
        return {
            "success": True,
            "address": address,
            "balance_eth": balance_eth,
            "balance_usd": balance_eth * 3500,  # Approximate ETH price
            "balance_wei": balance_wei
        }
        
    except Exception as e:
        return {
            "success": False,
            "address": address,
            "error": str(e),
            "balance_eth": 0.0,
            "balance_usd": 0.0
        }

def get_transaction_count(address: str) -> int:
    """Get transaction count (nonce) for address"""
    try:
        nonce = make_rpc_call("eth_getTransactionCount", [address, "latest"])
        return int(nonce, 16)
    except Exception:
        return 0

def get_latest_block_number() -> int:
    """Get latest block number"""
    try:
        block_number = make_rpc_call("eth_blockNumber")
        return int(block_number, 16)
    except Exception:
        return 0

def analyze_funds_web3(expected_amount: float, addresses: List[str]) -> Dict[str, Any]:
    """Analyze funds using Web3 RPC calls"""
    print(f"🔍 Analyzing {expected_amount:.6f} ETH across {len(addresses)} addresses")
    print(f"📡 Using Base RPC: {BASE_RPC_URL}")
    print("=" * 60)
    
    # Get network info
    try:
        latest_block = get_latest_block_number()
        print(f"📦 Latest Block: {latest_block}")
    except Exception as e:
        print(f"⚠️  Could not get block number: {e}")
    
    total_found = 0.0
    total_usd = 0.0
    address_results = []
    
    for i, address in enumerate(addresses, 1):
        print(f"\n📍 [{i}/{len(addresses)}] Checking {address[:10]}...{address[-8:]}")
        
        # Get balance
        balance_result = get_balance_web3(address)
        
        if balance_result["success"]:
            balance_eth = balance_result["balance_eth"]
            balance_usd = balance_result["balance_usd"]
            total_found += balance_eth
            total_usd += balance_usd
            
            # Get transaction count
            nonce = get_transaction_count(address)
            
            status = "✅" if balance_eth > 0 else "🔍"
            print(f"  {status} Balance: {balance_eth:.6f} ETH (${balance_usd:.2f})")
            print(f"  📝 Transaction Count: {nonce}")
            
            # Check if this matches your audit data
            if address == "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9":
                if abs(balance_eth - 0.009157) < 0.000001:
                    print(f"  📊 ✅ Matches audit data: 0.009157 ETH")
                else:
                    print(f"  📊 ⚠️  Audit data shows 0.009157 ETH, current: {balance_eth:.6f}")
            
            address_results.append({
                "address": address,
                "balance_eth": balance_eth,
                "balance_usd": balance_usd,
                "nonce": nonce,
                "success": True
            })
        else:
            print(f"  ❌ Error: {balance_result['error']}")
            address_results.append({
                "address": address,
                "balance_eth": 0.0,
                "balance_usd": 0.0,
                "nonce": 0,
                "success": False,
                "error": balance_result["error"]
            })
    
    # Calculate missing amount
    missing_eth = max(0, expected_amount - total_found)
    missing_usd = missing_eth * 3500
    
    print("\n" + "=" * 60)
    print(f"💰 Expected: {expected_amount:.6f} ETH (${expected_amount * 3500:.2f})")
    print(f"💰 Found: {total_found:.6f} ETH (${total_usd:.2f})")
    print(f"❌ Missing: {missing_eth:.6f} ETH (${missing_usd:.2f})")
    
    # Generate recommendations
    recommendations = []
    if missing_eth > 0:
        recommendations.append(f"Missing {missing_eth:.6f} ETH (${missing_usd:.2f})")
        
        # Check if you have enough for activation
        if total_found >= 0.016:  # Activation threshold
            recommendations.append("✅ Sufficient funds for StarkNet activation")
        else:
            needed = 0.016 - total_found
            recommendations.append(f"Need {needed:.6f} ETH more for activation (${needed * 3500:.2f})")
        
        # Check specific addresses
        main_wallet_balance = 0.0
        for result in address_results:
            if result["success"] and result["address"] == "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9":
                main_wallet_balance = result["balance_eth"]
                break
        
        if main_wallet_balance > 0:
            recommendations.append(f"Main wallet has {main_wallet_balance:.6f} ETH - ready for operations")
        
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
        "timestamp": datetime.now().isoformat(),
        "latest_block": latest_block if 'latest_block' in locals() else 0
    }

def check_bridge_status(phantom_address: str) -> Dict[str, Any]:
    """Check for potential bridge transactions"""
    print(f"\n🌉 Checking bridge activity for {phantom_address[:10]}...")
    
    # This is a simplified check - in reality you'd need to query specific bridge contracts
    # or use more sophisticated transaction filtering
    
    try:
        # Get transaction count as a proxy for activity
        nonce = get_transaction_count(phantom_address)
        
        if nonce > 0:
            print(f"  📝 Account has {nonce} transactions - activity detected")
            
            # For detailed bridge analysis, you'd need to:
            # 1. Get transaction history
            # 2. Filter for bridge contract interactions
            # 3. Check specific bridge addresses
            
            return {
                "has_activity": True,
                "transaction_count": nonce,
                "bridge_detected": "Unknown - requires detailed transaction analysis"
            }
        else:
            print(f"  📝 Account has no transactions")
            return {
                "has_activity": False,
                "transaction_count": 0,
                "bridge_detected": False
            }
            
    except Exception as e:
        print(f"  ❌ Error checking bridge status: {e}")
        return {
            "has_activity": False,
            "error": str(e)
        }

def main():
    if len(sys.argv) < 3:
        print("Usage: python web3_fund_tracker.py <expected_amount_eth> <addresses_comma_separated>")
        print("Example: python web3_fund_tracker.py 0.018 \"0x1234...,0x5678...\"")
        print("\nYour addresses from audit:")
        print("  Main: 0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9")
        print("  Ghost: 0x000000000000000000000000ff01e0776369ce51debb16dfb70f23c16d875463")
        print("  Phantom: 0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9")
        return
    
    try:
        expected_amount = float(sys.argv[1])
        addresses_input = sys.argv[2]
        
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
        analysis = analyze_funds_web3(expected_amount, valid_addresses)
        
        # Check bridge status for Phantom address
        phantom_addr = "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"
        if phantom_addr in valid_addresses:
            bridge_info = check_bridge_status(phantom_addr)
            analysis["bridge_check"] = bridge_info
        
        # Save analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/reports/web3_fund_analysis_{timestamp}.json"
        
        report_path = Path(output_file)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(analysis, indent=2))
        
        print(f"\n📄 Analysis saved to: {output_file}")
        
    except ValueError:
        print("❌ Invalid amount. Please provide a number in ETH.")
    except KeyboardInterrupt:
        print("\n⚠️  Analysis cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
