"""Rich-based dashboard for orchestrator/status display."""
from __future__ import annotations

from datetime import datetime
from typing import List, Tuple, Optional

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


class Dashboard:
    def __init__(self, roi_target: float = 15.0):
        self.console = console
        self.layout = Layout()
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3),
        )
        self.logs: List[Tuple[str, str]] = []
        self.max_logs = 10
        self.roi_current = 0.0
        self.roi_target = roi_target

    def generate_header(self, block: int, gas_gwei: float, eth_balance: float = 0.0):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right", ratio=1)

        risk_color = "green" if gas_gwei < 30 else "red"
        bal_color = "green" if eth_balance > 0.001 else "red"

        grid.add_row(
            f"🌍 [bold]stark_PyRust_Chain[/bold] | Block: [blue]{block}[/blue] | ETH: [{bal_color}]{eth_balance:.4f}[/{bal_color}]",
            f"⛽ Gas: [{risk_color}]{gas_gwei:.2f} Gwei[/{risk_color}] | Risk: [{risk_color}]{'LOW' if gas_gwei < 30 else 'HIGH'}[/{risk_color}]",
        )
        return Panel(grid, style="white on blue")

    def generate_body(self):
        table = Table(title="Activity Log", expand=True, box=box.SIMPLE)
        table.add_column("Time", style="dim", width=10)
        table.add_column("Message")

        for timestamp, msg in self.logs[-self.max_logs:]:
            table.add_row(timestamp, msg)

        return Panel(table, title="Strategy Execution", border_style="green")

    def generate_footer(self):
        progress = (self.roi_current / self.roi_target) * 100 if self.roi_target else 0.0
        return Panel(
            f"💰 ROI Progress: [bold green]${self.roi_current:.2f}[/bold green] / ${self.roi_target:.2f} ({progress:.1f}%)",
            style="white on black",
        )

    def log(self, message: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.logs.append((ts, message))

    def update_roi(self, profit_sway: float):
        # Assumption: 1000 SWAY = $1.00 (legacy heuristic)
        usd_value = profit_sway / 1000.0
        self.roi_current += usd_value

    def render(self, block: int, gas_gwei: float, eth_balance: float = 0.0):
        self.layout["header"].update(self.generate_header(block, gas_gwei, eth_balance))
        self.layout["body"].update(self.generate_body())
        self.layout["footer"].update(self.generate_footer())
        return self.layout
