#!/usr/bin/env python3
"""
PyPro Systems - Fund Tracker CLI Tool
Track and analyze missing funds across blockchain networks
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.etherscan_client import FundTracker, EtherscanClient
from foundation.constants import STARGATE_BRIDGE_ADDRESS

def parse_addresses(addresses_input: str) -> List[str]:
    """Parse addresses from various input formats"""
    addresses = []
    
    # Handle different input formats
    if "," in addresses_input:
        addresses = [addr.strip() for addr in addresses_input.split(",")]
    elif " " in addresses_input:
        addresses = addresses_input.split()
    else:
        addresses = [addresses_input.strip()]
    
    # Validate addresses - StarkNet addresses are 66 chars, Base/Ethereum are 42 chars
    valid_addresses = []
    for addr in addresses:
        addr = addr.strip()
        if addr.startswith("0x") and (len(addr) == 42 or len(addr) == 66):
            valid_addresses.append(addr)
        else:
            print(f"⚠️  Invalid address format: {addr} (expected 0x + 40 or 64 chars)")
    
    return valid_addresses

async def track_missing_funds(expected_amount: float, addresses: List[str], 
                            network: str = "base", output_file: str = None):
    """Track missing funds across addresses"""
    print(f"🔍 Tracking {expected_amount:.6f} ETH across {len(addresses)} addresses")
    print(f"📡 Network: {network.upper()}")
    print("=" * 60)
    
    tracker = FundTracker(network=network)
    analysis = await tracker.track_missing_funds(expected_amount, addresses)
    
    # Display results
    print(f"💰 Expected: {analysis['expected_amount_eth']:.6f} ETH (${analysis['expected_amount_usd']:.2f})")
    print(f"💰 Found: {analysis['total_found_eth']:.6f} ETH (${analysis['total_found_usd']:.2f})")
    print(f"❌ Missing: {analysis['missing_eth']:.6f} ETH (${analysis['missing_usd']:.2f})")
    print()
    
    print("📍 Address Breakdown:")
    for addr, data in analysis["address_breakdown"].items():
        if "balance_eth" in data:
            status = "✅" if data["balance_eth"] > 0 else "🔍"
            print(f"  {status} {addr[:10]}...{addr[-8:]}: {data['balance_eth']:.6f} ETH (${data['balance_usd']:.2f})")
        else:
            print(f"  ❌ {addr[:10]}...{addr[-8:]}: ERROR - {data['error']}")
    
    print()
    print("📋 Recommendations:")
    for i, rec in enumerate(analysis["recommendations"], 1):
        print(f"  {i}. {rec}")
    
    # Save detailed report
    if output_file:
        report_path = Path(output_file)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a simple report without EtherscanClient to avoid dependency issues
        simple_report = f"""# Missing Funds Analysis Report

**Generated**: {datetime.now().isoformat()}
**Expected Amount**: {analysis['expected_amount_eth']:.6f} ETH (${analysis['expected_amount_usd']:.2f})
**Total Found**: {analysis['total_found_eth']:.6f} ETH (${analysis['total_found_usd']:.2f})
**Missing**: {analysis['missing_eth']:.6f} ETH (${analysis['missing_usd']:.2f})

## Address Breakdown

"""
        
        for addr, data in analysis["address_breakdown"].items():
            if "balance_eth" in data:
                simple_report += f"### {addr[:10]}...{addr[-8:]}\n"
                simple_report += f"- **Balance**: {data['balance_eth']:.6f} ETH (${data['balance_usd']:.2f})\n"
                simple_report += f"- **Last Updated**: {data['last_updated']}\n\n"
            else:
                simple_report += f"### {addr[:10]}...{addr[-8:]}\n"
                simple_report += f"- **Error**: {data['error']}\n\n"
        
        simple_report += "## Recommendations\n\n"
        for i, rec in enumerate(analysis["recommendations"], 1):
            simple_report += f"{i}. {rec}\n"
        
        report_path.write_text(simple_report)
        print(f"\n📄 Detailed report saved to: {output_file}")
    
    return analysis

async def monitor_bridge(phantom_addr: str, starknet_addr: str, 
                        network: str = "base", timeout_minutes: int = 30):
    """Monitor bridge transaction status"""
    print(f"🌉 Monitoring bridge: {phantom_addr[:10]}... → {starknet_addr[:10]}...")
    print(f"⏱️  Timeout: {timeout_minutes} minutes")
    print("=" * 60)
    
    tracker = FundTracker(network=network)
    bridge_addr = STARGATE_BRIDGE_ADDRESS
    
    status = await tracker.monitor_bridge_recovery(
        phantom_addr, starknet_addr, bridge_addr
    )
    
    print(f"📊 Bridge Status: {status['status'].upper()}")
    
    if "latest_tx" in status:
        tx = status["latest_tx"]
        print(f"🔄 Latest Transaction:")
        print(f"  Hash: {tx['hash']}")
        print(f"  Value: {tx['value_eth']:.6f} ETH")
        print(f"  Timestamp: {tx['timestamp']}")
        print(f"  Confirmations: {tx['confirmations']}")
        print(f"  Success: {'✅' if tx['success'] else '❌'}")
    
    if "balances" in status:
        print(f"\n💰 Current Balances:")
        from_bal = status["balances"]["from_address"]
        to_bal = status["balances"]["to_address"]
        
        print(f"  From ({from_bal['address'][:10]}...): {from_bal['balance_eth']:.6f} ETH (${from_bal['balance_usd']:.2f})")
        print(f"  To ({to_bal['address'][:10]}...): {to_bal['balance_eth']:.6f} ETH (${to_bal['balance_usd']:.2f})")
    
    if "bridge_history" in status:
        print(f"\n📜 Bridge History:")
        for tx in status["bridge_history"]:
            status_icon = "✅" if tx["success"] else "❌"
            print(f"  {status_icon} {tx['timestamp']}: {tx['value']:.6f} ETH ({tx['confirmations']} confirmations)")
    
    return status

async def generate_report(addresses: List[str], network: str = "base", 
                         output_file: str = None):
    """Generate comprehensive fund report"""
    print(f"📊 Generating fund report for {len(addresses)} addresses")
    print(f"📡 Network: {network.upper()}")
    print("=" * 60)
    
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/reports/fund_report_{timestamp}.md"
    
    async with EtherscanClient(network) as client:
        report = await client.generate_fund_report(addresses, output_file)
    
    print(f"📄 Report generated: {output_file}")
    print("\n" + "=" * 60)
    print(report[:500] + "..." if len(report) > 500 else report)
    
    return report

async def check_specific_address(address: str, network: str = "base"):
    """Check specific address details"""
    print(f"🔍 Analyzing address: {address}")
    print(f"📡 Network: {network.upper()}")
    print("=" * 60)
    
    async with EtherscanClient(network) as client:
        # Get balance
        balance = await client.get_balance(address)
        print(f"💰 Balance: {balance.balance_eth:.6f} ETH (${balance.balance_usd:.2f})")
        print(f"📅 Last Updated: {balance.last_updated}")
        
        # Get recent transactions
        try:
            txs = await client.get_transactions(address, limit=10)
            print(f"\n📜 Recent Transactions ({len(txs)}):")
            
            for i, tx in enumerate(txs[:5], 1):
                status = "✅" if tx.status else "❌"
                print(f"  {i}. {status} {tx.timestamp.strftime('%Y-%m-%d %H:%M')} | "
                      f"{tx.value:.6f} ETH | {tx.tx_hash[:10]}...{tx.tx_hash[-8:]}")
                
        except Exception as e:
            print(f"❌ Failed to get transactions: {e}")
    
    return balance

def main():
    parser = argparse.ArgumentParser(description="Track and analyze blockchain funds")
    parser.add_argument("--network", default="base", choices=["base", "ethereum", "arbitrum", "optimism"],
                       help="Blockchain network to query")
    parser.add_argument("--output", "-o", help="Output file for reports")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Track missing funds command
    track_parser = subparsers.add_parser("track", help="Track missing funds")
    track_parser.add_argument("amount", type=float, help="Expected amount in ETH")
    track_parser.add_argument("addresses", help="Addresses to check (comma-separated)")
    track_parser.add_argument("--output", "-o", help="Output file for report")
    
    # Monitor bridge command
    bridge_parser = subparsers.add_parser("bridge", help="Monitor bridge transaction")
    bridge_parser.add_argument("phantom_addr", help="Phantom wallet address")
    bridge_parser.add_argument("starknet_addr", help="StarkNet address")
    bridge_parser.add_argument("--timeout", type=int, default=30, help="Timeout in minutes")
    
    # Generate report command
    report_parser = subparsers.add_parser("report", help="Generate fund report")
    report_parser.add_argument("addresses", help="Addresses to include (comma-separated)")
    
    # Check address command
    check_parser = subparsers.add_parser("check", help="Check specific address")
    check_parser.add_argument("address", help="Address to check")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "track":
            addresses = parse_addresses(args.addresses)
            if not addresses:
                print("❌ No valid addresses provided")
                return
            
            asyncio.run(track_missing_funds(
                args.amount, addresses, args.network, args.output
            ))
        
        elif args.command == "bridge":
            asyncio.run(monitor_bridge(
                args.phantom_addr, args.starknet_addr, args.network, args.timeout
            ))
        
        elif args.command == "report":
            addresses = parse_addresses(args.addresses)
            if not addresses:
                print("❌ No valid addresses provided")
                return
            
            asyncio.run(generate_report(addresses, args.network, args.output))
        
        elif args.command == "check":
            asyncio.run(check_specific_address(args.address, args.network))
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
