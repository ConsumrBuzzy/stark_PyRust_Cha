#!/usr/bin/env python3
"""
PyPro Systems - Bridge Status Checker
Check Base transaction logs for bridge completion clues
"""

import requests
import json
import sys
from pathlib import Path
from datetime import datetime

# Configuration
STARGATE_TX = "0x2dfc79aa3ad0ba437b7122a2b538eb72b2259f261a3f40818e7fa7a5074a64cd"
RHINO_TX = "0xb79f01bef77911dfb44e63909af4c74a533dd50eef681711298cf20d3f0809e2"

# Base RPC
BASE_RPC = "https://base.gateway.tenderly.co"

def get_transaction_receipt(tx_hash: str) -> dict:
    """Get transaction receipt with logs"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionReceipt",
            "params": [tx_hash],
            "id": 1
        }
        
        response = requests.post(BASE_RPC, json=payload, timeout=10)
        data = response.json()
        
        if "error" in data:
            return {"error": data["error"]}
        return {"result": data["result"]}
        
    except Exception as e:
        return {"error": str(e)}

def get_transaction_details(tx_hash: str) -> dict:
    """Get transaction details"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByHash",
            "params": [tx_hash],
            "id": 1
        }
        
        response = requests.post(BASE_RPC, json=payload, timeout=10)
        data = response.json()
        
        if "error" in data:
            return {"error": data["error"]}
        return {"result": data["result"]}
        
    except Exception as e:
        return {"error": str(e)}

def analyze_bridge_transaction(tx_hash: str, bridge_name: str) -> dict:
    """Analyze bridge transaction for completion clues"""
    print(f"🔍 ANALYZING {bridge_name} BRIDGE")
    print("=" * 50)
    print(f"Transaction: {tx_hash}")
    print(f"Explorer: https://basescan.org/tx/{tx_hash}")
    print()
    
    # Get transaction details
    tx_result = get_transaction_details(tx_hash)
    if "error" in tx_result:
        print(f"❌ Failed to get transaction details: {tx_result['error']}")
        return {"success": False, "error": tx_result["error"]}
    
    tx = tx_result["result"]
    
    # Get receipt with logs
    receipt_result = get_transaction_receipt(tx_hash)
    if "error" in receipt_result:
        print(f"❌ Failed to get receipt: {receipt_result['error']}")
        return {"success": False, "error": receipt_result["error"]}
    
    receipt = receipt_result["result"]
    
    print(f"📋 TRANSACTION DETAILS")
    print("-" * 25)
    print(f"Status: {'SUCCESS' if receipt.get('status') == '0x1' else 'FAILED'}")
    print(f"Block: {int(receipt.get('blockNumber', '0x0'), 16)}")
    print(f"Gas Used: {int(receipt.get('gasUsed', '0x0'), 16)}")
    print(f"From: {tx['from']}")
    print(f"To: {tx.get('to', 'Contract Deploy')}")
    print(f"Value: {int(tx['value'], 16) / 1e18:.6f} ETH")
    
    # Analyze logs for bridge completion clues
    logs = receipt.get("logs", [])
    print(f"\n📝 TRANSACTION LOGS ({len(logs)} found)")
    print("-" * 35)
    
    completion_clues = []
    error_clues = []
    
    for i, log in enumerate(logs, 1):
        address = log.get("address", "")
        topics = log.get("topics", [])
        data = log.get("data", "")
        
        print(f"\n{i}. Log Address: {address}")
        print(f"   Topics: {len(topics)} topics")
        
        # Check for common bridge completion patterns
        if any(topic.startswith("0x") and len(topic) > 10 for topic in topics):
            print(f"   Topics: {[topic[:10] + '...' for topic in topics[:3]]}")
        
        if data and len(data) > 10:
            print(f"   Data: {data[:50]}...")
        
        # Look for success indicators
        topics_str = str(topics).lower()
        data_str = data.lower()
        
        if any(keyword in topics_str or keyword in data_str for keyword in [
            "bridge", "mint", "transfer", "complete", "success", "received"
        ]):
            completion_clues.append({
                "address": address,
                "topics": topics,
                "data": data
            })
            print(f"   ✅ POTENTIAL SUCCESS CLUE")
        
        if any(keyword in topics_str or keyword in data_str for keyword in [
            "error", "fail", "revert", "insufficient", "timeout"
        ]):
            error_clues.append({
                "address": address,
                "topics": topics,
                "data": data
            })
            print(f"   ❌ POTENTIAL ERROR CLUE")
    
    # Analyze input data
    input_data = tx.get("input", "")
    print(f"\n🔍 INPUT DATA ANALYSIS")
    print("-" * 25)
    print(f"Input length: {len(input_data)} characters")
    
    if input_data:
        print(f"Input preview: {input_data[:100]}...")
        
        # Look for StarkNet address in input
        starknet_addr = "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
        if starknet_addr.lower() in input_data.lower():
            print(f"✅ StarkNet address found in input data!")
            print(f"   This confirms the bridge was for your account")
        else:
            print(f"⚠️  StarkNet address not found in input")
    
    # Summary
    print(f"\n📊 BRIDGE ANALYSIS SUMMARY")
    print("=" * 30)
    
    status = "UNKNOWN"
    confidence = "LOW"
    
    if receipt.get("status") == "0x1":
        status = "BASE_TX_SUCCESS"
        confidence = "MEDIUM"
        
        if completion_clues:
            status = "LIKELY_COMPLETED"
            confidence = "HIGH"
            print(f"✅ Transaction successful + completion clues found")
            print(f"   Bridge likely completed successfully")
        else:
            print(f"✅ Transaction successful but no clear completion clues")
            print(f"   Bridge may still be processing on L2")
    
    if error_clues:
        status = "LIKELY_FAILED"
        confidence = "HIGH"
        print(f"❌ Error clues detected in logs")
        print(f"   Bridge likely failed")
    
    print(f"Status: {status}")
    print(f"Confidence: {confidence}")
    print(f"Completion clues: {len(completion_clues)}")
    print(f"Error clues: {len(error_clues)}")
    
    return {
        "success": True,
        "tx_hash": tx_hash,
        "bridge_name": bridge_name,
        "status": status,
        "confidence": confidence,
        "completion_clues": completion_clues,
        "error_clues": error_clues,
        "base_tx_success": receipt.get("status") == "0x1",
        "logs_count": len(logs)
    }

def main():
    print("🚀 BRIDGE STATUS CHECKER")
    print("=" * 40)
    print("Analyzing bridge transactions for completion clues...")
    print()
    
    # Analyze StarkGate bridge
    starkgate_result = analyze_bridge_transaction(STARGATE_TX, "STARKGATE")
    
    print("\n" + "="*60 + "\n")
    
    # Analyze Rhino bridge
    rhino_result = analyze_bridge_transaction(RHINO_TX, "RHINO")
    
    # Final summary
    print("\n🎯 FINAL BRIDGE STATUS SUMMARY")
    print("=" * 40)
    
    total_bridged = 0.009 + 0.009168  # From transaction values
    
    print(f"Total bridged: {total_bridged:.6f} ETH")
    print()
    
    print(f"StarkGate Bridge:")
    print(f"  Status: {starkgate_result.get('status', 'UNKNOWN')}")
    print(f"  Confidence: {starkgate_result.get('confidence', 'LOW')}")
    print(f"  Base TX: {'✅ Success' if starkgate_result.get('base_tx_success') else '❌ Failed'}")
    print()
    
    print(f"Rhino Bridge:")
    print(f"  Status: {rhino_result.get('status', 'UNKNOWN')}")
    print(f"  Confidence: {rhino_result.get('confidence', 'LOW')}")
    print(f"  Base TX: {'✅ Success' if rhino_result.get('base_tx_success') else '❌ Failed'}")
    print()
    
    # Recommendations
    print(f"🎯 RECOMMENDATIONS")
    print("=" * 20)
    
    if starkgate_result.get("confidence") == "HIGH":
        print("✅ StarkGate bridge likely completed - funds should be on StarkNet")
        print("🔍 Try alternative StarkNet explorers when they're back online")
    else:
        print("⚠️  StarkGate bridge status unclear - monitor for completion")
    
    if rhino_result.get("confidence") == "HIGH":
        if rhino_result.get("status") == "LIKELY_COMPLETED":
            print("✅ Rhino bridge likely completed")
        else:
            print("❌ Rhino bridge likely failed - contact support")
    else:
        print("⚠️  Rhino bridge status unclear - monitor for completion")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/reports/bridge_status_{timestamp}.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "starkgate_analysis": starkgate_result,
        "rhino_analysis": rhino_result,
        "total_bridged": total_bridged
    }
    
    report_path = Path(output_file)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    
    print(f"\n📄 Report saved to: {output_file}")

if __name__ == "__main__":
    main()
