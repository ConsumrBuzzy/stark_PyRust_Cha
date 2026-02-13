#!/usr/bin/env python3
"""
War Room Dashboard - Professional Real-Time Monitoring
Integrates PhantomArbiter dashboard with StarkNet portfolio tracking
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add core to path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call

# Import dashboard and factory
from core.ui import get_dashboard
from core.factory import get_provider_factory

class WarRoomDashboard:
    """
    Professional real-time dashboard for StarkNet portfolio monitoring
    Integrates with PhantomArbiter dashboard architecture
    """
    
    def __init__(self):
        self.console = Console()
        self.dashboard = get_dashboard()
        self.provider_factory = get_provider_factory()
        
        # StarkNet configuration from environment
        self.main_wallet = os.getenv("STARKNET_WALLET_ADDRESS")
        self.ghost_address = "os.getenv("STARKNET_GHOST_ADDRESS")"
        self.eth_contract = int(os.getenv("STARKNET_ETH_CONTRACT", "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"), 16)
        
        # Validate configuration
        if not self.main_wallet:
            raise ValueError("STARKNET_WALLET_ADDRESS environment variable not set")
        
        # Monitoring state
        self.check_count = 0
        self.last_balances = {}
        self.alerts_sent = set()
        
        logger.info(f"🎯 War Room Dashboard initialized for {self.main_wallet[:10]}...")
    
    async def check_starknet_balances(self) -> Dict[str, float]:
        """Check balances using Shadow Protocol"""
        
        balances = {}
        
        try:
            # Get best provider
            provider_name, client = self.provider_factory.get_best_provider()
            
            # Check Main Wallet
            main_call = Call(
                to_addr=self.eth_contract,
                selector=get_selector_from_name("balanceOf"),
                calldata=[int(self.main_wallet, 16)]
            )
            
            main_result = await client.call_contract(main_call)
            main_balance = main_result[0] / 1e18
            balances["main_wallet"] = main_balance
            
            # Check Ghost Address
            ghost_call = Call(
                to_addr=self.eth_contract,
                selector=get_selector_from_name("balanceOf"),
                calldata=[int(self.ghost_address, 16)]
            )
            
            ghost_result = await client.call_contract(ghost_call)
            ghost_balance = ghost_result[0] / 1e18
            balances["ghost_address"] = ghost_balance
            
            logger.debug(f"✅ Balance check: Main={main_balance:.6f}, Ghost={ghost_balance:.6f}")
            
        except Exception as e:
            logger.error(f"❌ Balance check failed: {e}")
            balances["main_wallet"] = self.last_balances.get("main_wallet", 0.0)
            balances["ghost_address"] = self.last_balances.get("ghost_address", 0.0)
        
        self.last_balances = balances.copy()
        return balances
    
    def check_alerts(self, balances: Dict[str, float]) -> list:
        """Check for important alerts"""
        
        alerts = []
        
        # Ghost funds detection
        if balances.get("ghost_address", 0) >= 0.005:
            alert_key = "ghost_detected"
            if alert_key not in self.alerts_sent:
                alerts.append("🎉 GHOST FUNDS DETECTED!")
                self.alerts_sent.add(alert_key)
        
        # Activation readiness
        combined_balance = balances.get("main_wallet", 0) + balances.get("ghost_address", 0)
        if combined_balance >= 0.016:
            alert_key = "activation_ready"
            if alert_key not in self.alerts_sent:
                alerts.append("🚀 ACTIVATION WINDOW OPEN!")
                self.alerts_sent.add(alert_key)
        
        # Balance changes
        if self.check_count > 0:
            prev_ghost = self.last_balances.get("ghost_address", 0)
            curr_ghost = balances.get("ghost_address", 0)
            if curr_ghost != prev_ghost and curr_ghost > 0:
                alerts.append(f"💰 Ghost balance changed: {curr_ghost:.6f} ETH")
        
        return alerts
    
    async def update_dashboard_state(self):
        """Update dashboard with current state"""
        
        # Check balances
        balances = await self.check_starknet_balances()
        
        # Check alerts
        alerts = self.check_alerts(balances)
        
        # Create state for dashboard
        dashboard_state = {
            "starknet_balance": balances.get("main_wallet", 0.0),
            "ghost_balance": balances.get("ghost_address", 0.0),
            "provider_status": "Operational",
            "alerts": alerts,
            "check_count": self.check_count
        }
        
        # Update dashboard
        self.dashboard.update_state(dashboard_state)
        
        # Print alerts to console
        for alert in alerts:
            self.console.print(f"🚨 {alert}", style="bold yellow")
        
        self.check_count += 1
        
        return dashboard_state
    
    async def run_war_room(self, update_interval: int = 5):
        """Run the war room dashboard"""
        
        self.console.print(Panel.fit(
            "[bold blue]🎯 WAR ROOM DASHBOARD[/bold blue]\n"
            "PhantomArbiter Pattern | StarkNet Shadow Protocol\n"
            "Real-time Portfolio Monitoring & Activation Tracking\n"
            f"Main Wallet: {self.main_wallet[:10]}...\n"
            f"Ghost Address: {self.ghost_address[:10]}...",
            title="STARKNET COMMAND CENTER"
        ))
        
        # Initialize provider factory
        await self.provider_factory.check_all_providers()
        
        try:
            with Live(self.dashboard.layout, refresh_per_second=1, screen=True) as live:
                while True:
                    try:
                        # Update dashboard state
                        state = await self.update_dashboard_state()
                        
                        # Update layout
                        self.dashboard.update_layout()
                        
                        # Log periodic status
                        if self.check_count % 12 == 0:  # Every minute at 5s intervals
                            combined = state["starknet_balance"] + state["ghost_balance"]
                            logger.info(f"📊 Status Check #{self.check_count}: Combined {combined:.6f} ETH")
                        
                        await asyncio.sleep(update_interval)
                        
                    except KeyboardInterrupt:
                        break
                    except Exception as e:
                        logger.error(f"❌ Dashboard update error: {e}")
                        await asyncio.sleep(update_interval)
                        
        except KeyboardInterrupt:
            self.console.print("\n🛑 War Room stopped by user", style="bold yellow")
        
        # Final summary
        final_balances = await self.check_starknet_balances()
        combined_total = final_balances.get("main_wallet", 0) + final_balances.get("ghost_address", 0)
        
        self.console.print(Panel.fit(
            f"[bold green]WAR ROOM SESSION COMPLETE[/bold green]\n\n"
            f"Total Checks: {self.check_count}\n"
            f"Final Balance: {combined_total:.6f} ETH (${combined_total * 2200:.2f})\n"
            f"Main Wallet: {final_balances.get('main_wallet', 0):.6f} ETH\n"
            f"Ghost Address: {final_balances.get('ghost_address', 0):.6f} ETH\n"
            f"Alerts Triggered: {len(self.alerts_sent)}\n\n"
            f"[dim]Session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
            title="SESSION SUMMARY"
        ))

async def main():
    """Main execution"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="War Room Dashboard")
    parser.add_argument("--interval", type=int, default=5, help="Update interval in seconds")
    args = parser.parse_args()
    
    console = Console()
    console.print("🎯 War Room Dashboard - PhantomArbiter Pattern", style="bold blue")
    console.print("Real-time StarkNet portfolio monitoring", style="dim")
    
    try:
        war_room = WarRoomDashboard()
        await war_room.run_war_room(args.interval)
        
    except Exception as e:
        console.print(f"❌ Fatal error: {e}", style="bold red")
        logger.error(f"❌ War Room error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 War Room stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
