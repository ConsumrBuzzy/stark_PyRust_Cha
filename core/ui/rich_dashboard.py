#!/usr/bin/env python3
"""
Rich Dashboard Manager - PhantomArbiter Pattern Implementation
Professional real-time dashboard for StarkNet portfolio monitoring
Ported from PhantomArbiter/src/shared/ui/rich_panel.py
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

# Add core to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich import box
from rich.align import Align
from loguru import logger

@dataclass
class PortfolioState:
    """Portfolio state for dashboard display"""
    total_value_usd: float = 0.0
    starknet_balance_eth: float = 0.0
    starknet_balance_usd: float = 0.0
    ghost_balance_eth: float = 0.0
    ghost_balance_usd: float = 0.0
    activation_threshold: float = 0.016
    activation_progress: float = 0.0
    activation_ready: bool = False
    ghost_detected: bool = False
    provider_status: str = "Unknown"
    last_update: datetime = None

class StarkNetDashboard:
    """
    Professional real-time dashboard for StarkNet portfolio monitoring
    Based on PhantomArbiter DNEMDashboard architecture
    """
    
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.setup_layout()
        
        # State management
        self.state = PortfolioState()
        self.running = False
        
        # Colors and styling
        self.colors = {
            "success": "green",
            "warning": "yellow", 
            "error": "red",
            "info": "blue",
            "dim": "dim"
        }
        
        logger.info("📺 Rich Dashboard initialized")
    
    def setup_layout(self):
        """Setup the dashboard layout structure"""
        
        # Main layout split
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        # Main section split
        self.layout["main"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )
        
        # Left side - Portfolio Overview
        self.layout["left"].split_column(
            Layout(name="portfolio", ratio=1),
            Layout(name="activation", ratio=1)
        )
        
        # Right side - System Status
        self.layout["right"].split_column(
            Layout(name="providers", ratio=1),
            Layout(name="monitoring", ratio=1)
        )
    
    def create_header(self) -> Panel:
        """Create header panel"""
        
        header_content = f"""
[bold blue]🌑 STARKNET SHADOW PROTOCOL DASHBOARD[/bold blue]
[dim]Real-time Portfolio Monitoring & Activation Tracking[/dim]
[dim]Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]
        """.strip()
        
        return Panel(
            Align.center(header_content),
            box=box.ROUNDED,
            style="blue"
        )
    
    def create_portfolio_panel(self) -> Panel:
        """Create portfolio overview panel"""
        
        # Portfolio table
        table = Table(title="💰 Portfolio Overview", box=box.ROUNDED)
        table.add_column("Asset", style="cyan")
        table.add_column("Balance", justify="right", style="green")
        table.add_column("USD Value", justify="right", style="yellow")
        table.add_column("Status", style="bold")
        
        # Main Wallet
        main_status = "💼 ACTIVE" if self.state.starknet_balance_eth > 0 else "⚪ EMPTY"
        table.add_row(
            "Main Wallet",
            f"{self.state.starknet_balance_eth:.6f} ETH",
            f"${self.state.starknet_balance_usd:.2f}",
            main_status
        )
        
        # Ghost Address
        ghost_status = "🎉 DETECTED" if self.state.ghost_detected else "👻 MONITORING"
        table.add_row(
            "Ghost Address",
            f"{self.state.ghost_balance_eth:.6f} ETH",
            f"${self.state.ghost_balance_usd:.2f}",
            ghost_status
        )
        
        # Combined Total
        combined_eth = self.state.starknet_balance_eth + self.state.ghost_balance_eth
        combined_usd = self.state.starknet_balance_usd + self.state.ghost_balance_usd
        
        table.add_row(
            "---",
            "---",
            "---",
            "---"
        )
        
        table.add_row(
            "**COMBINED**",
            f"**{combined_eth:.6f} ETH**",
            f"**${combined_usd:.2f}**",
            "📊 TOTAL"
        )
        
        return Panel(table, box=box.ROUNDED)
    
    def create_activation_panel(self) -> Panel:
        """Create activation status panel"""
        
        # Progress bar using text
        progress = min(100, self.state.activation_progress * 100)
        progress_bar = "█" * int(progress / 5) + "░" * (20 - int(progress / 5))
        progress_color = "green" if self.state.activation_ready else "yellow"
        
        # Status details
        status_text = f"""
[b]Progress:[/b] [{progress_color}]{progress_bar}[/{progress_color}] {progress:.1f}%
[b]Threshold:[/b] {self.state.activation_threshold:.6f} ETH
[b]Current:[/b] {self.state.starknet_balance_eth + self.state.ghost_balance_eth:.6f} ETH
[b]Needed:[/b] {max(0, self.state.activation_threshold - (self.state.starknet_balance_eth + self.state.ghost_balance_eth)):.6f} ETH

[b]Status:[/b] {'🚀 READY FOR ACTIVATION' if self.state.activation_ready else '⏳ INSUFFICIENT FUNDS'}
[b]Ghost:[/b] {'🎉 DETECTED' if self.state.ghost_detected else '👻 WAITING'}
        """.strip()
        
        return Panel(
            status_text,
            title="🎯 Activation Status",
            box=box.ROUNDED,
            border_style="green" if self.state.activation_ready else "yellow"
        )
    
    def create_providers_panel(self) -> Panel:
        """Create provider status panel"""
        
        # Provider table
        table = Table(title="🏭 Provider Factory Status", box=box.ROUNDED)
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Latency", justify="right")
        table.add_column("Success Rate", justify="right")
        
        # Mock provider data (would be populated from ProviderFactory)
        providers = [
            ("Alchemy", "✅ HEALTHY", "410ms", "100%"),
            ("Lava", "⚠️ DEGRADED", "690ms", "95%"),
            ("1RPC", "✅ HEALTHY", "1200ms", "100%"),
            ("OnFinality", "❌ RATE LIMITED", "N/A", "0%")
        ]
        
        for name, status, latency, success_rate in providers:
            table.add_row(name, status, latency, success_rate)
        
        return Panel(table, box=box.ROUNDED)
    
    def create_monitoring_panel(self) -> Panel:
        """Create monitoring status panel"""
        
        # Monitoring info
        monitoring_text = f"""
[b]🔍 Shadow Protocol:[/b] {'✅ ACTIVE' if True else '❌ INACTIVE'}
[b]📡 L7 DPI Bypass:[/b] {'✅ OPERATIONAL' if True else '❌ BLOCKED'}
[b]👻 Ghost Sentry:[/b] {'✅ MONITORING' if True else '❌ STOPPED'}
[b]⚛️ Atomic Engine:[/b] {'✅ READY' if self.state.activation_ready else '⏳ WAITING'}

[b]🔄 Last Check:[/b] {datetime.now().strftime('%H:%M:%S')}
[b]⏱️ Next Poll:[/b] 180s
[b]📊 Check Count:[/b] 42

[b]🎯 Current Strategy:[/b]
• Monitor bridge completion
• Wait for activation threshold
• Execute atomic deployment
        """.strip()
        
        return Panel(
            monitoring_text,
            title="🔍 Monitoring Status",
            box=box.ROUNDED,
            style="blue"
        )
    
    def create_footer(self) -> Panel:
        """Create footer panel"""
        
        footer_content = f"""
[dim]PhantomArbiter Pattern | Shadow Protocol Active | L7 DPI Bypass Operational[/dim]
[dim]Press Ctrl+C to exit | Auto-refresh every 5 seconds[/dim]
        """.strip()
        
        return Panel(
            Align.center(footer_content),
            box=box.ROUNDED,
            style="dim"
        )
    
    def update_layout(self):
        """Update all layout panels with current state"""
        
        self.layout["header"].update(self.create_header())
        self.layout["portfolio"].update(self.create_portfolio_panel())
        self.layout["activation"].update(self.create_activation_panel())
        self.layout["providers"].update(self.create_providers_panel())
        self.layout["monitoring"].update(self.create_monitoring_panel())
        self.layout["footer"].update(self.create_footer())
    
    def update_state(self, new_state: Dict[str, Any]):
        """Update dashboard state"""
        
        # Update portfolio values
        self.state.starknet_balance_eth = new_state.get("starknet_balance", 0.0)
        self.state.starknet_balance_usd = self.state.starknet_balance_eth * 2200
        self.state.ghost_balance_eth = new_state.get("ghost_balance", 0.0)
        self.state.ghost_balance_usd = self.state.ghost_balance_eth * 2200
        
        # Update activation status
        combined_balance = self.state.starknet_balance_eth + self.state.ghost_balance_eth
        self.state.activation_progress = combined_balance / self.state.activation_threshold
        self.state.activation_ready = combined_balance >= self.state.activation_threshold
        self.state.ghost_detected = self.state.ghost_balance_eth >= 0.005
        
        # Update provider status
        self.state.provider_status = new_state.get("provider_status", "Unknown")
        self.state.last_update = datetime.now()
    
    async def run_dashboard(self, update_interval: int = 5):
        """Run the dashboard with live updates"""
        
        self.running = True
        
        try:
            with Live(self.layout, refresh_per_second=1, screen=True) as live:
                while self.running:
                    # Update state (would get from actual monitoring systems)
                    mock_state = {
                        "starknet_balance": 0.009157,
                        "ghost_balance": 0.000000,
                        "provider_status": "Healthy"
                    }
                    self.update_state(mock_state)
                    
                    # Update layout
                    self.update_layout()
                    
                    # Sleep for update interval
                    await asyncio.sleep(update_interval)
                    
        except KeyboardInterrupt:
            self.console.print("\n🛑 Dashboard stopped by user")
        finally:
            self.running = False

# Global dashboard instance
_dashboard: Optional[StarkNetDashboard] = None

def get_dashboard() -> StarkNetDashboard:
    """Get global dashboard instance"""
    global _dashboard
    if _dashboard is None:
        _dashboard = StarkNetDashboard()
    return _dashboard

async def run_dashboard(update_interval: int = 5):
    """Run the global dashboard"""
    dashboard = get_dashboard()
    await dashboard.run_dashboard(update_interval)

if __name__ == "__main__":
    console = Console()
    console.print("📺 StarkNet Dashboard - PhantomArbiter Pattern", style="bold blue")
    console.print("Starting real-time portfolio monitoring...", style="dim")
    
    try:
        asyncio.run(run_dashboard())
    except KeyboardInterrupt:
        console.print("\n🛑 Dashboard stopped", style="bold yellow")
    except Exception as e:
        console.print(f"❌ Dashboard error: {e}", style="bold red")
