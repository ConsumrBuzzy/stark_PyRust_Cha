#!/usr/bin/env python3
"""
Combined Audit - Multi-Address Balance Aggregation
Monitors combined balance across Main Wallet and Ghost Address for activation triggers
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add core to path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.ops.audit_ops import run_audit, build_tables
from src.ops.env import build_config

class CombinedAuditor:
    """Aggregates balances across multiple StarkNet addresses"""
    
    def __init__(self):
        self.console = Console()
        self.setup_logging()
        cfg = build_config()

        self.main_wallet = cfg.starknet_address
        self.ghost_address = os.getenv("STARKNET_GHOST_ADDRESS") or cfg.phantom_address
        self.activation_threshold = float(os.getenv("ACTIVATION_THRESHOLD", 0.016))
        self.ghost_threshold = float(os.getenv("GHOST_THRESHOLD", 0.005))

        # Statistics
        self.check_count = 0
        self.last_combined_balance = 0.0
        
        logger.info("🔍 Combined Auditor initialized")
        logger.info(f"💼 Main Wallet: {self.main_wallet}")
        logger.info(f"👻 Ghost Address: {self.ghost_address}")
        logger.info(f"🎯 Activation Threshold: {self.activation_threshold} ETH")
    
    def setup_logging(self):
        """Configure logging"""
        logger.remove()
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level="INFO"
        )
        
        # File logging
        logger.add(
            "combined_audit.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level="DEBUG",
            rotation="5 MB",
            retention="3 days"
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
    
    async def check_all_balances(self) -> Dict[str, float]:
        """Check balances using ops.audit_ops (one-shot)."""
        result = await run_audit(ghost_address=self.ghost_address, main_address=self.main_wallet)
        return {
            "main_wallet": float(result.main_balance_eth),
            "ghost_address": float(result.ghost_balance_eth),
        }
    
    def create_balance_table(self, balances: Dict[str, float]) -> Table:
        """Create comprehensive balance table"""
        
        table = Table(title="💰 Combined Balance Audit")
        table.add_column("Address", style="cyan")
        table.add_column("Label", style="white")
        table.add_column("ETH Balance", justify="right", style="green")
        table.add_column("USD Value", justify="right", style="yellow")
        table.add_column("Status", style="bold")
        
        # Main Wallet
        main_balance = balances.get("main_wallet", 0.0)
        main_usd = main_balance * 2200
        main_status = "💼 ACTIVE" if main_balance > 0 else "⚪ EMPTY"
        
        table.add_row(
            self.main_wallet[:10] + "...",
            "Main Wallet",
            f"{main_balance:.6f}",
            f"${main_usd:.2f}",
            main_status
        )
        
        # Ghost Address
        ghost_balance = balances.get("ghost_address", 0.0)
        ghost_usd = ghost_balance * 2200
        ghost_status = "🎉 DETECTED" if ghost_balance >= self.ghost_threshold else "⏳ MONITORING"
        
        table.add_row(
            self.ghost_address[:10] + "...",
            "Ghost Address",
            f"{ghost_balance:.6f}",
            f"${ghost_usd:.2f}",
            ghost_status
        )
        
        # Combined Total
        combined_balance = main_balance + ghost_balance
        combined_usd = combined_balance * 2200
        
        table.add_row(
            "---",
            "COMBINED TOTAL",
            f"{combined_balance:.6f}",
            f"${combined_usd:.2f}",
            "📊 AGGREGATE"
        )
        
        return table
    
    def analyze_activation_readiness(self, balances: Dict[str, float]) -> Dict:
        """Analyze if activation conditions are met"""
        
        main_balance = balances.get("main_wallet", 0.0)
        ghost_balance = balances.get("ghost_address", 0.0)
        combined_balance = main_balance + ghost_balance
        
        analysis = {
            "combined_balance": combined_balance,
            "activation_ready": False,
            "ghost_ready": False,
            "recommendations": [],
            "urgency": "LOW"
        }
        
        # Check activation threshold
        if combined_balance >= self.activation_threshold:
            analysis["activation_ready"] = True
            analysis["recommendations"].append("🚀 ACTIVATION WINDOW OPEN!")
            analysis["recommendations"].append(f"💰 Combined: {combined_balance:.6f} ETH >= {self.activation_threshold} ETH")
            analysis["urgency"] = "HIGH"
        else:
            needed = self.activation_threshold - combined_balance
            analysis["recommendations"].append(f"⏳ Need {needed:.6f} more ETH for activation")
            analysis["urgency"] = "MEDIUM" if combined_balance > 0.01 else "LOW"
        
        # Check Ghost threshold
        if ghost_balance >= self.ghost_threshold:
            analysis["ghost_ready"] = True
            analysis["recommendations"].append("🎉 GHOST FUNDS READY FOR SWEEP")
        else:
            analysis["recommendations"].append(f"👻 Ghost: {ghost_balance:.6f} ETH (need {self.ghost_threshold} ETH)")
        
        # Strategic insights
        if main_balance > 0 and ghost_balance == 0:
            analysis["recommendations"].append("💼 Main wallet funded - waiting for Ghost bridge")
        elif main_balance == 0 and ghost_balance > 0:
            analysis["recommendations"].append("👻 Ghost funds arrived - need more for activation")
        elif main_balance > 0 and ghost_balance > 0:
            analysis["recommendations"].append("💰 Both addresses funded - check activation threshold")
        
        return analysis
    
    def create_activation_panel(self, analysis: Dict) -> Panel:
        """Create activation readiness panel"""
        
        combined = analysis["combined_balance"]
        threshold = self.activation_threshold
        progress = min(100, (combined / threshold) * 100)
        
        content = f"""
**Combined Balance**: {combined:.6f} ETH (${combined * 2200:.2f})
**Activation Threshold**: {threshold:.6f} ETH
**Progress**: {progress:.1f}%

**Status**: {'🚀 READY FOR ACTIVATION' if analysis['activation_ready'] else '⏳ INSUFFICIENT FUNDS'}

**Ghost Funds**: {'🎉 DETECTED' if analysis['ghost_ready'] else '👻 PENDING'}
**Urgency**: {analysis['urgency']}
"""
        
        border_style = {
            "HIGH": "green",
            "MEDIUM": "yellow",
            "LOW": "blue"
        }.get(analysis["urgency"], "white")
        
        return Panel(
            content.strip(),
            title="🎯 Activation Analysis",
            border_style=border_style
        )
    
    def save_audit_report(self, balances: Dict[str, float], analysis: Dict):
        """Save combined audit report"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# Combined Balance Audit Report

**Timestamp**: {timestamp}
**Method**: Shadow Protocol (L7 DPI Bypass)
**Purpose**: Activation Readiness Assessment

## Balance Breakdown

| Address | Label | ETH Balance | USD Value | Status |
|---------|-------|-------------|-----------|--------|
| {self.main_wallet} | Main Wallet | {balances.get('main_wallet', 0):.6f} | ${balances.get('main_wallet', 0) * 2200:.2f} | {'Active' if balances.get('main_wallet', 0) > 0 else 'Empty'} |
| {self.ghost_address} | Ghost Address | {balances.get('ghost_address', 0):.6f} | ${balances.get('ghost_address', 0) * 2200:.2f} | {'Detected' if balances.get('ghost_address', 0) >= self.ghost_threshold else 'Monitoring'} |
| --- | **COMBINED TOTAL** | **{analysis['combined_balance']:.6f}** | **${analysis['combined_balance'] * 2200:.2f}** | **Aggregate** |

## Activation Analysis

**Threshold**: {self.activation_threshold} ETH
**Current**: {analysis['combined_balance']:.6f} ETH
**Status**: {'READY' if analysis['activation_ready'] else 'INSUFFICIENT'}

### Recommendations
"""
        
        for rec in analysis['recommendations']:
            report += f"- {rec}\n"
        
        report += f"""

## Strategic Position

### Main Wallet ({self.main_wallet})
- **Balance**: {balances.get('main_wallet', 0):.6f} ETH
- **Status**: {'Ready for activation if deployed' if balances.get('main_wallet', 0) > 0 else 'Empty'}

### Ghost Address ({self.ghost_address})
- **Balance**: {balances.get('ghost_address', 0):.6f} ETH
- **Status**: {'Ready for sweep' if balances.get('ghost_address', 0) >= self.ghost_threshold else 'Waiting for bridge'}

### Next Steps

1. **If Activation Ready**: Run `python tools/activate.py`
2. **If Insufficient**: Wait for bridge completion or add more funds
3. **If Ghost Detected**: Run sweep commands when ready

## Technical Notes

This audit uses the Shadow Protocol to bypass L7 DPI filtering.
Balances are verified via ERC-20 contract calls rather than account state queries.

---
*Generated by tools/combined_audit.py - Multi-Address Aggregation*
"""
        
        # Save to data/reports directory
        reports_dir = Path(__file__).parent.parent / "data" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"combined_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📄 Combined audit report saved: {report_file}")
    
    async def run_continuous_audit(self, interval: int = 300):
        """Run continuous audit with activation alerts"""
        
        self.console.print(Panel.fit(
            "[bold blue]🔍 COMBINED AUDITOR - CONTINUOUS[/bold blue]\n"
            "Multi-Address Balance Aggregation\n"
            f"Main Wallet: {self.main_wallet[:10]}...\n"
            f"Ghost Address: {self.ghost_address[:10]}...\n"
            f"Activation Threshold: {self.activation_threshold} ETH\n"
            f"Poll Interval: {interval}s",
            title="Activation Monitor"
        ))
        
        while True:
            self.check_count += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            logger.info(f"🔍 Combined Audit #{self.check_count} - {timestamp}")
            
            # Check all balances
            balances = await self.check_all_balances()
            
            # Display results
            table = self.create_balance_table(balances)
            self.console.print(table)
            
            # Analyze activation readiness
            analysis = self.analyze_activation_readiness(balances)
            activation_panel = self.create_activation_panel(analysis)
            self.console.print(activation_panel)
            
            # Check for activation trigger
            if analysis["activation_ready"]:
                self.console.print(Panel.fit(
                    "[bold green]🚀 ACTIVATION WINDOW OPEN![/bold green]\n\n"
                    f"Combined Balance: {analysis['combined_balance']:.6f} ETH\n"
                    f"Threshold Met: {self.activation_threshold} ETH\n\n"
                    "[bold yellow]Run: python tools/activate.py[/bold yellow]",
                    title="ACTIVATION TRIGGER",
                    border_style="green"
                ))
                
                logger.success(f"🚀 ACTIVATION TRIGGER: {analysis['combined_balance']:.6f} ETH available")
                
                # Save trigger report
                self.save_audit_report(balances, analysis)
                
                # Optional: Break or continue monitoring
                # break  # Uncomment to stop after trigger
            
            # Check for Ghost funds
            if analysis["ghost_ready"] and not hasattr(self, 'ghost_alerted'):
                self.console.print(Panel.fit(
                    "[bold green]🎉 GHOST FUNDS DETECTED![/bold green]\n\n"
                    f"Ghost Balance: {balances.get('ghost_address', 0):.6f} ETH\n"
                    "Ready for sweep execution",
                    title="GHOST TRIGGER",
                    border_style="green"
                ))
                
                logger.success(f"🎉 GHOST FUNDS: {balances.get('ghost_address', 0):.6f} ETH detected")
                self.ghost_alerted = True
            
            # Save periodic reports
            if self.check_count % 10 == 0:
                self.save_audit_report(balances, analysis)
            
            # Wait for next check
            logger.info(f"⏳ Waiting {interval}s for next audit...")
            await asyncio.sleep(interval)

async def main():
    """Main execution"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Combined Balance Auditor")
    parser.add_argument("--continuous", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=300, help="Poll interval in seconds")
    args = parser.parse_args()
    
    console = Console()
    console.print("🔍 Combined Auditor - Multi-Address Balance Aggregation", style="bold blue")
    console.print("🎯 Activation Readiness Assessment", style="dim")
    
    auditor = CombinedAuditor()
    
    if args.continuous:
        await auditor.run_continuous_audit(args.interval)
    else:
        # Single audit
        balances = await auditor.check_all_balances()
        table = auditor.create_balance_table(balances)
        console.print(table)
        
        analysis = auditor.analyze_activation_readiness(balances)
        panel = auditor.create_activation_panel(analysis)
        console.print(panel)
        
        auditor.save_audit_report(balances, analysis)
        
        console.print("✅ Combined audit complete!", style="bold green")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Combined audit stopped by user")
    except Exception as e:
        logger.error(f"❌ Combined audit error: {e}")
        sys.exit(1)
