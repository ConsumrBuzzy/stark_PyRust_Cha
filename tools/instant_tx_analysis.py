#!/usr/bin/env python3
"""
PyPro Systems - Instant Transaction Analysis
Direct analysis of provided transaction data
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

def analyze_transactions():
    """Analyze the provided transaction data"""
    print("⚡ INSTANT TRANSACTION ANALYSIS")
    print("=" * 50)
    
    # Transaction data from user
    transactions = [
        {
            "hash": "0x2dfc79aa3ad0ba437b7122a2b538eb72b2259f261a3f40818e7fa7a5074a64cd",
            "block": 42091705,
            "time_ago": "14 hrs ago",
            "direction": "OUT",
            "from": "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9",
            "to": "0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419",  # StarkGate Bridge
            "value": 0.009,
            "type": "STARKGATE_BRIDGE"
        },
        {
            "hash": "0xb79f01bef77911dfb44e63909af4c74a533dd50eef681711298cf20d3f0809e2",
            "block": 42040678,
            "time_ago": "43 hrs ago",
            "direction": "OUT",
            "from": "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9",
            "to": "Rhino.fi: Bridge",
            "value": 0.009168,
            "type": "RHINO_BRIDGE"
        },
        {
            "hash": "0x6e68dd6d0574ea6d131df00846c98194cb57693983b05995478663af2f125978",
            "block": 42040579,
            "time_ago": "43 hrs ago",
            "direction": "IN",
            "from": "Coinbase",
            "to": "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9",
            "value": 0.0091663,
            "type": "COINBASE_DEPOSIT"
        },
        {
            "hash": "0xb35e4e1b11a228f3d80260168245f0515f21fbfd4794b515c7bea81b4cfb5e46",
            "block": 42090867,
            "time_ago": "15 hrs ago",
            "direction": "IN",
            "from": "0x26b610a0...907917419",
            "to": "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9",
            "value": 0.01471479,
            "type": "INCOMING_TRANSFER"
        }
    ]
    
    print("📋 TRANSACTION BREAKDOWN")
    print("=" * 30)
    
    total_sent = 0.0
    total_received = 0.0
    bridge_count = 0
    bridge_amounts = []
    
    for i, tx in enumerate(transactions, 1):
        print(f"{i}. {tx['hash'][:10]}... | {tx['direction']} | {tx['value']:.6f} ETH")
        print(f"   Type: {tx['type']}")
        print(f"   Time: {tx['time_ago']}")
        print(f"   To: {tx['to'][:20]}...")
        print(f"   Explorer: https://basescan.org/tx/{tx['hash']}")
        
        if tx['direction'] == 'OUT':
            total_sent += tx['value']
            if 'BRIDGE' in tx['type']:
                bridge_count += 1
                bridge_amounts.append(tx['value'])
        else:
            total_received += tx['value']
        
        print()
    
    print("💰 FINANCIAL ANALYSIS")
    print("=" * 30)
    print(f"Total Sent: {total_sent:.6f} ETH")
    print(f"Total Received: {total_received:.6f} ETH")
    print(f"Net Flow: {total_received - total_sent:+.6f} ETH")
    print(f"Bridge Transactions: {bridge_count}")
    print(f"Bridge Amounts: {bridge_amounts}")
    
    # Missing funds calculation
    current_balance = 0.005715  # From previous analysis
    expected_initial = 0.018
    
    total_outflow = total_sent
    total_inflow = total_received
    
    print(f"\n🔍 MISSING FUNDS ANALYSIS")
    print("=" * 30)
    print(f"Expected (initial): {expected_initial:.6f} ETH")
    print(f"Current balance: {current_balance:.6f} ETH")
    print(f"Total sent: {total_sent:.6f} ETH")
    print(f"Total received: {total_received:.6f} ETH")
    
    # Calculate what should be there
    calculated_balance = expected_initial - total_sent + total_received
    actual_missing = calculated_balance - current_balance
    
    print(f"Calculated balance: {calculated_balance:.6f} ETH")
    print(f"Actual balance: {current_balance:.6f} ETH")
    print(f"Missing: {actual_missing:.6f} ETH (${actual_missing * 3500:.2f})")
    
    # Bridge analysis
    if bridge_count > 0:
        print(f"\n🌉 BRIDGE ANALYSIS")
        print("=" * 20)
        
        total_bridged = sum(bridge_amounts)
        print(f"Total bridged: {total_bridged:.6f} ETH")
        print(f"Bridge transactions:")
        
        for tx in transactions:
            if 'BRIDGE' in tx['type']:
                print(f"  {tx['hash'][:10]}... | {tx['value']:.6f} ETH | {tx['type']}")
                print(f"    Time: {tx['time_ago']} | Status: NEEDS INVESTIGATION")
        
        # Check if bridge amounts match missing
        if abs(total_bridged - actual_missing) < 0.001:
            print(f"\n✅ BRIDGE AMOUNTS MATCH MISSING FUNDS!")
            print(f"🔍 Your {total_bridged:.6f} ETH is likely stuck in bridge contracts")
            print(f"💡 ACTION NEEDED: Check bridge contract status")
        else:
            print(f"\n⚠️  Bridge total ({total_bridged:.6f}) ≠ missing ({actual_missing:.6f})")
    
    # Specific transaction analysis
    print(f"\n🎯 CRITICAL TRANSACTIONS")
    print("=" * 30)
    
    # StarkGate bridge (most recent)
    starkgate_tx = None
    for tx in transactions:
        if tx['type'] == 'STARKGATE_BRIDGE':
            starkgate_tx = tx
            break
    
    if starkgate_tx:
        print(f"🔴 STARKGATE BRIDGE (14 hrs ago)")
        print(f"   Hash: {starkgate_tx['hash']}")
        print(f"   Amount: {starkgate_tx['value']:.6f} ETH")
        print(f"   To: 0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419")
        print(f"   Status: ⚠️  LIKELY STUCK - needs immediate investigation")
        print(f"   Action: Check if funds arrived on StarkNet")
    
    # Rhino bridge
    rhino_tx = None
    for tx in transactions:
        if tx['type'] == 'RHINO_BRIDGE':
            rhino_tx = tx
            break
    
    if rhino_tx:
        print(f"\n🟡 RHINO BRIDGE (43 hrs ago)")
        print(f"   Hash: {rhino_tx['hash']}")
        print(f"   Amount: {rhino_tx['value']:.6f} ETH")
        print(f"   Status: ⚠️  LIKELY STUCK - needs investigation")
    
    print(f"\n🎯 IMMEDIATE ACTIONS REQUIRED")
    print("=" * 35)
    print("1. 🔴 URGENT: Check StarkGate bridge status")
    print(f"   Transaction: {starkgate_tx['hash'] if starkgate_tx else 'N/A'}")
    print(f"   StarkNet address: 0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9")
    print()
    print("2. 🟡 MEDIUM: Check Rhino bridge status")
    print(f"   Transaction: {rhino_tx['hash'] if rhino_tx else 'N/A'}")
    print()
    print("3. 🟢 LOW: Monitor for bridge completion")
    print("   Bridge transactions can take 30min-2hrs to complete")
    
    # Save analysis
    report = {
        "timestamp": datetime.now().isoformat(),
        "analysis_type": "DIRECT_USER_DATA",
        "transactions": transactions,
        "total_sent": total_sent,
        "total_received": total_received,
        "current_balance": current_balance,
        "missing_funds": actual_missing,
        "bridge_count": bridge_count,
        "bridge_amounts": bridge_amounts,
        "critical_transactions": {
            "starkgate": starkgate_tx,
            "rhino": rhino_tx
        }
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/reports/direct_tx_analysis_{timestamp}.json"
    
    report_path = Path(output_file)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    
    print(f"\n📄 Analysis saved to: {output_file}")
    
    return report

def main():
    analyze_transactions()

if __name__ == "__main__":
    main()
