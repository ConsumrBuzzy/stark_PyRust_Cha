#!/usr/bin/env python3
"""
Simple Starknet RPC check using requests only
No complex dependencies - just direct JSON-RPC calls
"""

import requests
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def check_starknet_balance(address: str, label: str) -> dict:
    """Check ETH balance using direct JSON-RPC call"""
    
    rpc_url = "https://starknet-mainnet.public.blastapi.io"
    
    # ETH token contract address on Starknet
    eth_contract = "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"
    
    payload = {
        "jsonrpc": "2.0",
        "method": "starknet_call",
        "params": {
            "request": {
                "contract_address": eth_contract,
                "entry_point_selector": "0x02e4266535d4c6e9360c72f3db4e0a9a3c6fb4d4eb8c4be0659c5f8629a8a2d4",  # balanceOf
                "calldata": [address, 0]
            },
            "block_number": "latest"
        },
        "id": 1
    }
    
    try:
        response = requests.post(rpc_url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if "result" in result and len(result["result"]) > 0:
            balance_hex = result["result"][0]
            balance_wei = int(balance_hex, 16)
            balance_eth = balance_wei / 1e18
            
            return {
                "address": address,
                "label": label,
                "balance_eth": balance_eth,
                "balance_wei": balance_wei,
                "status": "success"
            }
        else:
            return {
                "address": address,
                "label": label,
                "balance_eth": 0.0,
                "balance_wei": 0,
                "status": "no_balance_data"
            }
            
    except Exception as e:
        return {
            "address": address,
            "label": label,
            "balance_eth": 0.0,
            "balance_wei": 0,
            "status": f"error: {str(e)}"
        }

def check_deployment_status(address: str) -> dict:
    """Check if account is deployed by checking contract class"""
    
    rpc_url = "https://starknet-mainnet.public.blastapi.io"
    
    payload = {
        "jsonrpc": "2.0",
        "method": "starknet_getClassAt",
        "params": {
            "contract_address": address,
            "block_number": "latest"
        },
        "id": 1
    }
    
    try:
        response = requests.post(rpc_url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if "result" in result:
            return {
                "address": address,
                "deployed": True,
                "status": "deployed"
            }
        else:
            return {
                "address": address,
                "deployed": False,
                "status": "not_deployed"
            }
            
    except Exception as e:
        # If we get an error, likely not deployed
        return {
            "address": address,
            "deployed": False,
            "status": f"not_deployed: {str(e)[:50]}"
        }

def main():
    """Main execution"""
    console.print("🔍 Starknet Real-Time Audit (Direct RPC)", style="bold blue")
    
    # Target addresses
    ghost_address = "0xfF01E0776369Ce51debb16DFb70F23c16d875463"
    main_wallet = "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
    
    console.print(f"Ghost Address: {ghost_address}")
    console.print(f"Main Wallet: {main_wallet}")
    console.print()
    
    # Check balances
    ghost_result = check_starknet_balance(ghost_address, "Ghost Address")
    main_result = check_starknet_balance(main_wallet, "Main Wallet")
    
    # Check deployment status
    deployment_result = check_deployment_status(main_wallet)
    
    # Display results
    table = Table(title="Balance Check")
    table.add_column("Address", style="cyan")
    table.add_column("Label", style="magenta")
    table.add_column("ETH Balance", justify="right", style="green")
    table.add_column("Status", style="yellow")
    
    table.add_row(
        ghost_result["address"][:10] + "...",
        ghost_result["label"],
        f"{ghost_result['balance_eth']:.6f}",
        ghost_result["status"]
    )
    
    table.add_row(
        main_result["address"][:10] + "...",
        main_result["label"],
        f"{main_result['balance_eth']:.6f}",
        main_result["status"]
    )
    
    console.print(table)
    
    # Deployment status
    status_text = "✅ DEPLOYED" if deployment_result["deployed"] else "❌ NOT DEPLOYED"
    console.print(Panel(
        f"Main Wallet Status: {status_text}\nAddress: {deployment_result['address']}",
        title="🚀 Deployment Status",
        border_style="green" if deployment_result["deployed"] else "red"
    ))
    
    # Strategic analysis
    console.print("\n📊 Strategic Analysis:", style="bold")
    
    if ghost_result["balance_eth"] > 0.005:
        console.print(f"🎯 BRIDGE DETECTED: {ghost_result['balance_eth']:.6f} ETH at Ghost address", style="green")
    else:
        console.print(f"⏳ No bridge funds detected at Ghost address", style="yellow")
    
    if main_result["balance_eth"] > 0 and not deployment_result["deployed"]:
        console.print(f"⚠️  LOCKED FUNDS: {main_result['balance_eth']:.6f} ETH in undeployed wallet", style="yellow")
    elif main_result["balance_eth"] > 0 and deployment_result["deployed"]:
        console.print(f"✅ ACTIVE FUNDS: {main_result['balance_eth']:.6f} ETH in deployed wallet", style="green")
    else:
        console.print(f"💸 No funds in main wallet", style="red")
    
    # Save report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""# Starknet Audit Report

**Timestamp**: {timestamp}

## Balance Check

| Address | Label | ETH Balance | Status |
|---------|-------|-------------|--------|
| {ghost_result['address']} | {ghost_result['label']} | {ghost_result['balance_eth']:.6f} | {ghost_result['status']} |
| {main_result['address']} | {main_result['label']} | {main_result['balance_eth']:.6f} | {main_result['status']} |

## Deployment Status

- **Main Wallet**: {status_text}
- **Address**: {deployment_result['address']}

## Strategic Notes

"""
    
    if ghost_result["balance_eth"] > 0.005:
        report += f"- 🎯 Bridge funds detected: {ghost_result['balance_eth']:.6f} ETH\n"
    else:
        report += "- ⏳ No bridge funds detected\n"
    
    if main_result["balance_eth"] > 0 and not deployment_result["deployed"]:
        report += f"- ⚠️ Locked funds: {main_result['balance_eth']:.6f} ETH in undeployed wallet\n"
    elif main_result["balance_eth"] > 0 and deployment_result["deployed"]:
        report += f"- ✅ Active funds: {main_result['balance_eth']:.6f} ETH\n"
    else:
        report += "- 💸 No funds in main wallet\n"
    
    report += f"\n---\n*Generated by simple_starknet_check.py*"
    
    with open("starknet_audit_simple.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    console.print(f"\n📄 Report saved to: starknet_audit_simple.md")

if __name__ == "__main__":
    main()
