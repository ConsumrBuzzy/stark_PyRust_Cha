from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich import box
from datetime import datetime
import time

class Dashboard:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )
        self.logs = []
        self.max_logs = 10
        self.roi_current = 0.0
        self.roi_target = 15.0 # $15.00

    def generate_header(self, block, gas_gwei, eth_balance=0.0):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right", ratio=1)
        
        risk_color = "green" if gas_gwei < 30 else "red"
        bal_color = "green" if eth_balance > 0.001 else "red"
        
        grid.add_row(
            f"🌍 [bold]stark_PyRust_Chain[/bold] | Block: [blue]{block}[/blue] | ETH: [{bal_color}]{eth_balance:.4f}[/{bal_color}]",
            f"⛽ Gas: [{risk_color}]{gas_gwei:.2f} Gwei[/{risk_color}] | Risk: [{risk_color}]{'LOW' if gas_gwei < 30 else 'HIGH'}[/{risk_color}]"
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
        progress = (self.roi_current / self.roi_target) * 100
        return Panel(
            f"💰 ROI Progress: [bold green]${self.roi_current:.2f}[/bold green] / ${self.roi_target:.2f} ({progress:.1f}%)",
            style="white on black"
        )

    def log(self, message):
        ts = datetime.now().strftime("%H:%M:%S")
        self.logs.append((ts, message))

    def update_roi(self, profit_sway):
        # Assumption: 1000 SWAY = $1.00 (Example rate)
        usd_value = profit_sway / 1000.0 
        self.roi_current += usd_value

    def render(self, block, gas_gwei, eth_balance=0.0):
        self.layout["header"].update(self.generate_header(block, gas_gwei, eth_balance))
        self.layout["body"].update(self.generate_body())
        self.layout["footer"].update(self.generate_footer())
        return self.layout

if __name__ == "__main__":
    # Test Run
    dash = Dashboard()
    with Live(dash.render(0, 0), refresh_per_second=4) as live:
        for i in range(10):
            dash.log(f"Test Log {i}")
            dash.update_roi(50) # +0.05
            live.update(dash.render(600000+i, 15.5 + i))
            time.sleep(0.5)
