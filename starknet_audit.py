#!/usr/bin/env python3
"""
Real-time Starknet Balance Auditor
Checks Ghost address and main wallet without mock data
"""

import asyncio
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Load environment variables
load_dotenv()

class StarknetAuditor:
    """Direct Starknet RPC auditor for specific addresses"""
    
    def __init__(self):
        self.console = Console()
        self.rpc_url = os.getenv("STARKNET_RPC_URL", "https://starknet-mainnet.public.blastapi.io")
        
        # Target addresses from user request
        self.ghost_address = "0xfF01E0776369Ce51debb16DFb70F23c16d875463"
        self.main_wallet = "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
        
        logger.info("Starknet auditor initialized")
        logger.info("Ghost address: {}", self.ghost_address)
        logger.info("Main wallet: {}", self.main_wallet)
    
    async def check_balance(self, address: str, label: str) -> dict:
        """Check balance for a specific address using starknet.py"""
        try:
            # Import starknet.py here to avoid dependency issues
            from starknet_py.net.account.account import Account
            from starknet_py.net.full_node_client import FullNodeClient
            from starknet_py.net.models.chains import StarknetChainId
            
            client = FullNodeClient(node_url=self.rpc_url)
            
            # Get ETH balance directly
            balance_response = await client.get_balance(
                contract_address=address,
                block_number="latest"
            )
            
            # Convert from wei to ETH
            balance_eth = balance_response / 1e18
            
            result = {
                "address": address,
                "label": label,
                "balance_eth": balance_eth,
                "balance_wei": balance_response,
                "status": "success",
                "timestamp": datetime.now()
            }
            
            logger.info("{}: {:.6f} ETH", label, balance_eth)
            return result
            
        except Exception as e:
            logger.error("Failed to check {}: {}", label, str(e))
            return {
                "address": address,
                "label": label,
                "balance_eth": 0.0,
                "balance_wei": 0,
                "status": f"error: {str(e)}",
                "timestamp": datetime.now()
            }
    
    async def check_deployment_status(self, address: str) -> dict:
        """Check if account is deployed by checking contract code"""
        try:
            from starknet_py.net.full_node_client import FullNodeClient
            
            client = FullNodeClient(node_url=self.rpc_url)
            
            # Try to get contract code - if it exists, account is deployed
            code_response = await client.get_class_at(
                contract_address=address,
                block_number="latest"
            )
            
            result = {
                "address": address,
                "deployed": True,
                "class_hash": code_response,
                "status": "deployed"
            }
            
            logger.info("Account {} is DEPLOYED", address)
            return result
            
        except Exception as e:
            # If we can't get class, account is likely not deployed
            result = {
                "address": address,
                "deployed": False,
                "class_hash": None,
                "status": f"not_deployed: {str(e)}"
            }
            
            logger.info("Account {} is NOT DEPLOYED", address)
            return result
    
    async def run_audit(self):
        """Run complete audit of both addresses"""
        logger.info("Starting Starknet audit...")
        
        # Check balances for both addresses
        ghost_balance_task = self.check_balance(self.ghost_address, "Ghost Address")
        main_balance_task = self.check_balance(self.main_wallet, "Main Wallet")
        
        # Check deployment status for main wallet
        deployment_task = self.check_deployment_status(self.main_wallet)
        
        # Run all checks concurrently
        ghost_result, main_result, deployment_result = await asyncio.gather(
            ghost_balance_task,
            main_balance_task,
            deployment_task,
            return_exceptions=True
        )
        
        return {
            "ghost_balance": ghost_result,
            "main_balance": main_result,
            "deployment_status": deployment_result,
            "audit_timestamp": datetime.now()
        }
    
    def display_results(self, results: dict):
        """Display audit results in rich format"""
        # Main panel
        panel_content = f"Audit completed at: {results['audit_timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.console.print(Panel(
            panel_content,
            title="🔍 Starknet Real-Time Audit",
            border_style="blue"
        ))
        
        # Results table
        table = Table(title="Address Balance Check")
        table.add_column("Address", style="cyan")
        table.add_column("Label", style="magenta")
        table.add_column("ETH Balance", justify="right", style="green")
        table.add_column("Status", style="yellow")
        
        # Ghost address
        ghost = results["ghost_balance"]
        table.add_row(
            ghost["address"][:10] + "...",
            ghost["label"],
            f"{ghost['balance_eth']:.6f}",
            ghost["status"]
        )
        
        # Main wallet
        main = results["main_balance"]
        table.add_row(
            main["address"][:10] + "...",
            main["label"],
            f"{main['balance_eth']:.6f}",
            main["status"]
        )
        
        self.console.print(table)
        
        # Deployment status
        deployment = results["deployment_status"]
        status_text = "✅ DEPLOYED" if deployment["deployed"] else "❌ NOT DEPLOYED"
        
        self.console.print(Panel(
            f"Main Wallet Status: {status_text}\nAddress: {deployment['address']}",
            title="🚀 Deployment Status",
            border_style="green" if deployment["deployed"] else "red"
        ))
        
        # Strategic summary
        ghost_balance = results["ghost_balance"]["balance_eth"]
        main_balance = results["main_balance"]["balance_eth"]
        is_deployed = results["deployment_status"]["deployed"]
        
        if ghost_balance > 0.005:  # If bridge funds arrived
            self.console.print(f"🎯 **BRIDGE DETECTED**: {ghost_balance:.6f} ETH at Ghost address", style="green")
        
        if main_balance > 0 and not is_deployed:
            self.console.print(f"⚠️  **LOCKED FUNDS**: {main_balance:.6f} ETH in undeployed wallet", style="yellow")
        
        if is_deployed:
            self.console.print("✅ **READY**: Wallet is deployed and ready for transactions", style="green")
    
    def save_report(self, results: dict):
        """Save audit report to file"""
        report_path = Path("starknet_audit_report.md")
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Starknet Audit Report\n\n")
            f.write(f"**Timestamp**: {results['audit_timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Balance Check\n\n")
            f.write("| Address | Label | ETH Balance | Status |\n")
            f.write("|---------|-------|-------------|--------|\n")
            
            ghost = results["ghost_balance"]
            main = results["main_balance"]
            
            f.write(f"| {ghost['address']} | {ghost['label']} | {ghost['balance_eth']:.6f} | {ghost['status']} |\n")
            f.write(f"| {main['address']} | {main['label']} | {main['balance_eth']:.6f} | {main['status']} |\n\n")
            
            f.write("## Deployment Status\n\n")
            deployment = results["deployment_status"]
            status_text = "DEPLOYED" if deployment["deployed"] else "NOT DEPLOYED"
            f.write(f"- **Main Wallet**: {status_text}\n")
            f.write(f"- **Address**: {deployment['address']}\n\n")
            
            f.write("## Strategic Notes\n\n")
            if ghost["balance_eth"] > 0.005:
                f.write(f"- 🎯 Bridge funds detected: {ghost['balance_eth']:.6f} ETH\n")
            
            if main["balance_eth"] > 0 and not deployment["deployed"]:
                f.write(f"- ⚠️ Locked funds: {main['balance_eth']:.6f} ETH in undeployed wallet\n")
            
            if deployment["deployed"]:
                f.write("- ✅ Wallet ready for transactions\n")
            
            f.write(f"\n---\n*Generated by starknet_audit.py*")
        
        logger.info("Audit report saved to {}", report_path)
        return report_path

async def main():
    """Main execution"""
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    auditor = StarknetAuditor()
    results = await auditor.run_audit()
    
    auditor.display_results(results)
    report_path = auditor.save_report(results)
    
    print(f"\n📄 Audit report saved to: {report_path}")

if __name__ == "__main__":
    import sys
    asyncio.run(main())
