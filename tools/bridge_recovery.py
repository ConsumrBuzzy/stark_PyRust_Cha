#!/usr/bin/env python3
"""
Bridge Recovery Monitor - Base & StarkNet Cross-Chain Verification
Monitors stuck Orbiter bridge transactions and provides recovery insights
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

# Add core to path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from web3 import Web3
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call

class BridgeRecoveryMonitor:
    """Cross-chain bridge transaction recovery analyzer"""
    
    def __init__(self):
        self.console = Console()
        self.setup_logging()
        self.load_env()
        
        # Bridge transaction details
        self.base_tx_hash = "0x2dec7c24a1b11c731a25fd8c7c2e681488e0c58730ba82f9d20d46032a263407"
        self.transit_evm_address = "0xfF01E0776369Ce51debb16DFb70F23c16d875463"
        self.ghost_starknet_address = "os.getenv("STARKNET_GHOST_ADDRESS")"
        self.expected_amount = 0.006  # ETH
        
        # Network configurations
        self.base_rpc = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
        self.starknet_rpc = os.getenv("STARKNET_MAINNET_URL")
        
        # Initialize Web3 connections
        self.base_web3 = Web3(Web3.HTTPProvider(self.base_rpc))
        self.starknet_client = FullNodeClient(node_url=self.starknet_rpc) if self.starknet_rpc else None
        
        # ERC-20 contracts
        self.base_eth_contract = "0x4200000000000000000000000000000000000006"  # Base WETH
        self.starknet_eth_contract = int(os.getenv("STARKNET_ETH_CONTRACT", "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"), 16)
        
        logger.info("🌉 Bridge Recovery Monitor initialized")
        logger.info(f"🔍 Base TX: {self.base_tx_hash}")
        logger.info(f"👻 Ghost: {self.ghost_starknet_address}")
    
    def setup_logging(self):
        """Configure logging"""
        logger.remove()
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level="INFO"
        )
    
    def load_env(self):
        """Load environment variables"""
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key.strip()] = value.strip()
    
    async def check_base_transaction(self) -> Dict:
        """Check Base network transaction status"""
        
        try:
            # Get transaction details
            tx = self.base_web3.eth.get_transaction(self.base_tx_hash)
            tx_receipt = self.base_web3.eth.get_transaction_receipt(self.base_tx_hash)
            
            # Determine transaction status
            if tx_receipt.status == 1:
                status = "✅ SUCCESS"
                status_detail = "Transaction confirmed on Base"
            elif tx_receipt.status == 0:
                status = "❌ FAILED"
                status_detail = "Transaction failed on Base"
            else:
                status = "⏳ PENDING"
                status_detail = "Transaction still processing"
            
            # Extract key details
            result = {
                "hash": self.base_tx_hash,
                "status": status,
                "detail": status_detail,
                "block_number": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed,
                "from_address": tx["from"],
                "to_address": tx["to"],
                "value": self.base_web3.from_wei(tx["value"], "ether"),
                "timestamp": datetime.fromtimestamp(self.base_web3.eth.get_block(tx_receipt.blockNumber).timestamp)
            }
            
            # Check for refund events
            logs = tx_receipt.logs
            refund_detected = False
            for log in logs:
                if log.address.lower() == self.transit_evm_address.lower():
                    refund_detected = True
                    break
            
            result["refund_detected"] = refund_detected
            
            return result
            
        except Exception as e:
            logger.error(f"Base transaction check failed: {e}")
            return {
                "hash": self.base_tx_hash,
                "status": "❌ ERROR",
                "detail": f"Failed to check: {str(e)[:50]}...",
                "error": True
            }
    
    async def check_base_balance(self) -> Dict:
        """Check Base address balance for refunds"""
        
        try:
            balance_wei = self.base_web3.eth.get_balance(self.transit_evm_address)
            balance_eth = self.base_web3.from_wei(balance_wei, "ether")
            
            return {
                "address": self.transit_evm_address,
                "balance_eth": float(balance_eth),
                "balance_wei": balance_wei,
                "status": "✅ CHECKED"
            }
            
        except Exception as e:
            logger.error(f"Base balance check failed: {e}")
            return {
                "address": self.transit_evm_address,
                "balance_eth": 0.0,
                "status": f"❌ ERROR: {str(e)[:30]}..."
            }
    
    async def check_starknet_balance(self) -> Dict:
        """Check StarkNet Ghost address balance"""
        
        if not self.starknet_client:
            return {
                "address": self.ghost_starknet_address,
                "balance_eth": 0.0,
                "status": "❌ NO STARKNET RPC"
            }
        
        try:
            # Use shadow protocol (ERC-20 contract call)
            call = Call(
                to_addr=self.starknet_eth_contract,
                selector=get_selector_from_name("balanceOf"),
                calldata=[int(self.ghost_starknet_address, 16)]
            )
            
            result = await self.starknet_client.call_contract(call)
            balance_wei = result[0]
            balance_eth = balance_wei / 1e18
            
            return {
                "address": self.ghost_starknet_address,
                "balance_eth": balance_eth,
                "balance_wei": balance_wei,
                "status": "✅ CHECKED"
            }
            
        except Exception as e:
            logger.error(f"StarkNet balance check failed: {e}")
            return {
                "address": self.ghost_starknet_address,
                "balance_eth": 0.0,
                "status": f"❌ ERROR: {str(e)[:30]}..."
            }
    
    def analyze_bridge_status(self, base_tx: Dict, base_balance: Dict, starknet_balance: Dict) -> Dict:
        """Analyze overall bridge status and provide recovery recommendations"""
        
        analysis = {
            "overall_status": "UNKNOWN",
            "recovery_strategy": [],
            "urgency": "LOW",
            "next_steps": []
        }
        
        # Check Base transaction status
        if base_tx.get("status") == "✅ SUCCESS":
            analysis["overall_status"] = "BASE_CONFIRMED"
            analysis["recovery_strategy"].append("✅ Base transaction confirmed - funds sent to Orbiter")
            analysis["next_steps"].append("Monitor StarkNet for arrival (6-12 hours typical)")
            
            # Check StarkNet balance
            if starknet_balance.get("balance_eth", 0) >= self.expected_amount:
                analysis["overall_status"] = "COMPLETE"
                analysis["recovery_strategy"].append("🎉 Funds arrived on StarkNet!")
                analysis["urgency"] = "NONE"
            else:
                analysis["recovery_strategy"].append("⏳ Funds still in transit on StarkNet")
                analysis["urgency"] = "MEDIUM"
                
        elif base_tx.get("status") == "❌ FAILED":
            analysis["overall_status"] = "BASE_FAILED"
            analysis["recovery_strategy"].append("❌ Base transaction failed - check for refund")
            analysis["urgency"] = "HIGH"
            analysis["next_steps"].append("Check Base address for refund")
            analysis["next_steps"].append("Contact Orbiter support if no refund")
            
        elif base_tx.get("status") == "⏳ PENDING":
            analysis["overall_status"] = "BASE_PENDING"
            analysis["recovery_strategy"].append("⏳ Base transaction still processing")
            analysis["urgency"] = "LOW"
            analysis["next_steps"].append("Wait for Base confirmation")
        
        # Check for refunds
        if base_tx.get("refund_detected"):
            analysis["recovery_strategy"].append("💰 Refund detected on Base")
            analysis["next_steps"].append("Check Base balance for returned funds")
        
        # Check Base balance for unexpected refunds
        if base_balance.get("balance_eth", 0) > 0.001:  # More than dust
            analysis["recovery_strategy"].append(f"💰 Base balance: {base_balance['balance_eth']:.6f} ETH")
            if analysis["overall_status"] == "BASE_FAILED":
                analysis["next_steps"].append("Refund received - bridge failed safely")
        
        return analysis
    
    def create_status_table(self, base_tx: Dict, base_balance: Dict, starknet_balance: Dict) -> Table:
        """Create comprehensive status table"""
        
        table = Table(title="🌉 Bridge Recovery Status")
        table.add_column("Network", style="cyan")
        table.add_column("Component", style="white")
        table.add_column("Status", style="bold")
        table.add_column("Details", style="dim")
        
        # Base transaction
        table.add_row(
            "Base",
            "Transaction",
            base_tx.get("status", "❌ UNKNOWN"),
            base_tx.get("detail", "No details")
        )
        
        # Base balance
        base_bal_status = f"{base_balance.get('balance_eth', 0):.6f} ETH"
        table.add_row(
            "Base",
            "Balance",
            base_balance.get("status", "❌ UNKNOWN"),
            base_bal_status
        )
        
        # StarkNet balance
        stark_bal_status = f"{starknet_balance.get('balance_eth', 0):.6f} ETH"
        table.add_row(
            "StarkNet",
            "Ghost Balance",
            starknet_balance.get("status", "❌ UNKNOWN"),
            stark_bal_status
        )
        
        return table
    
    def create_recovery_panel(self, analysis: Dict) -> Panel:
        """Create recovery recommendations panel"""
        
        content = f"""
**Overall Status**: {analysis['overall_status']}

**Recovery Strategy**:
"""
        
        for strategy in analysis['recovery_strategy']:
            content += f"• {strategy}\n"
        
        if analysis['next_steps']:
            content += "\n**Next Steps**:\n"
            for step in analysis['next_steps']:
                content += f"• {step}\n"
        
        content += f"\n**Urgency**: {analysis['urgency']}"
        
        border_style = {
            "HIGH": "red",
            "MEDIUM": "yellow", 
            "LOW": "blue",
            "NONE": "green"
        }.get(analysis['urgency'], "white")
        
        return Panel(
            content.strip(),
            title="🔧 Recovery Analysis",
            border_style=border_style
        )
    
    def save_recovery_report(self, base_tx: Dict, base_balance: Dict, starknet_balance: Dict, analysis: Dict):
        """Save detailed recovery report"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# Bridge Recovery Report

**Timestamp**: {timestamp}
**Bridge**: Orbiter (Base → StarkNet)
**Transaction**: {self.base_tx_hash}
**Expected Amount**: {self.expected_amount} ETH

## Transaction Analysis

### Base Network
- **Status**: {base_tx.get('status', 'UNKNOWN')}
- **Detail**: {base_tx.get('detail', 'No details')}
- **Block**: {base_tx.get('block_number', 'N/A')}
- **Gas Used**: {base_tx.get('gas_used', 'N/A')}
- **From**: {base_tx.get('from_address', 'N/A')}
- **To**: {base_tx.get('to_address', 'N/A')}
- **Value**: {base_tx.get('value', 'N/A')} ETH
- **Timestamp**: {base_tx.get('timestamp', 'N/A')}
- **Refund Detected**: {base_tx.get('refund_detected', False)}

### Balance Status
- **Base Address**: {base_balance.get('address', 'N/A')}
- **Base Balance**: {base_balance.get('balance_eth', 0):.6f} ETH
- **StarkNet Ghost**: {starknet_balance.get('address', 'N/A')}
- **StarkNet Balance**: {starknet_balance.get('balance_eth', 0):.6f} ETH

## Recovery Analysis

**Overall Status**: {analysis['overall_status']}
**Urgency**: {analysis['urgency']}

### Recovery Strategies
"""
        
        for strategy in analysis['recovery_strategy']:
            report += f"- {strategy}\n"
        
        report += "\n### Recommended Actions\n"
        for step in analysis['next_steps']:
            report += f"- {step}\n"
        
        report += f"""

## Technical Notes

This analysis uses:
- Base network RPC for transaction verification
- StarkNet Shadow Protocol for balance checking
- Cross-chain correlation for recovery insights

## Support Information

If funds don't arrive within 24 hours:
1. Contact Orbiter support with transaction hash
2. Provide this report as evidence
3. Monitor for automatic refunds

**Orbiter Support**: Check their Discord or official channels
**Maker Address**: Extracted from Base transaction details

---
*Generated by tools/bridge_recovery.py - Cross-Chain Recovery Monitor*
"""
        
        # Save to data/reports directory
        reports_dir = Path(__file__).parent.parent / "data" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"bridge_recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📄 Recovery report saved: {report_file}")
    
    async def run_recovery_analysis(self):
        """Run complete bridge recovery analysis"""
        
        self.console.print(Panel.fit(
            "[bold blue]🌉 BRIDGE RECOVERY MONITOR[/bold blue]\n"
            "Cross-Chain Transaction Analysis\n"
            f"Base TX: {self.base_tx_hash[:10]}...\n"
            f"Expected: {self.expected_amount} ETH",
            title="Orbiter Bridge Recovery"
        ))
        
        # Check all components
        self.console.print("🔍 Analyzing bridge transaction...")
        
        # Parallel checks
        base_tx_task = self.check_base_transaction()
        base_balance_task = self.check_base_balance()
        starknet_balance_task = self.check_starknet_balance()
        
        base_tx, base_balance, starknet_balance = await asyncio.gather(
            base_tx_task,
            base_balance_task,
            starknet_balance_task
        )
        
        # Display results
        status_table = self.create_status_table(base_tx, base_balance, starknet_balance)
        self.console.print(status_table)
        
        # Analyze and provide recommendations
        analysis = self.analyze_bridge_status(base_tx, base_balance, starknet_balance)
        recovery_panel = self.create_recovery_panel(analysis)
        self.console.print(recovery_panel)
        
        # Save report
        self.save_recovery_report(base_tx, base_balance, starknet_balance, analysis)
        
        # Final recommendations
        if analysis['urgency'] == 'HIGH':
            self.console.print("\n🚨 HIGH URGENCY - Immediate action required", style="bold red")
        elif analysis['urgency'] == 'MEDIUM':
            self.console.print("\n⚠️ MEDIUM URGENCY - Monitor closely", style="bold yellow")
        else:
            self.console.print("\n✅ LOW URGENCY - Continue monitoring", style="bold green")

async def main():
    """Main execution"""
    
    console = Console()
    console.print("🌉 Bridge Recovery Monitor - Cross-Chain Analysis", style="bold blue")
    console.print("🔍 Orbiter Bridge Transaction Recovery", style="dim")
    
    monitor = BridgeRecoveryMonitor()
    await monitor.run_recovery_analysis()
    
    console.print("✅ Bridge recovery analysis complete!", style="bold green")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bridge recovery analysis stopped by user")
    except Exception as e:
        logger.error(f"❌ Bridge recovery error: {e}")
        sys.exit(1)
