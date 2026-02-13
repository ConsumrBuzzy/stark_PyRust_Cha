"""Influence strategy engine (legacy refinement loop) extracted from python-logic."""
from __future__ import annotations

import os
import time
import json
from typing import Optional, Callable
from rich.console import Console
from rich.panel import Panel

try:
    import stark_pyrust_chain
except ImportError:  # pragma: no cover - optional Rust bindings
    stark_pyrust_chain = None

console = Console()


class BaseStrategy:
    def __init__(self, dry_run: bool = True, log_fn: Optional[Callable[[str], None]] = None):
        self.dry_run = dry_run
        self.log_fn = log_fn or (lambda msg: console.print(f"[dim]{msg}[/dim]"))

    def log(self, message: str) -> None:
        self.log_fn(message)


class RefiningStrategy(BaseStrategy):
    """Automates the Iron -> Steel refining loop using Rust bindings."""

    def __init__(self, dry_run: bool = True, log_fn: Optional[Callable[[str], None]] = None):
        super().__init__(dry_run, log_fn)
        if not stark_pyrust_chain:
            raise RuntimeError("stark_pyrust_chain bindings not available")

        self.client = stark_pyrust_chain.PyInfluenceClient()
        self.graph = stark_pyrust_chain.PySupplyChain()
        rpc_url = os.getenv("STARKNET_MAINNET_URL") or os.getenv("STARKNET_RPC_URL")
        self.starknet = stark_pyrust_chain.PyStarknetClient(rpc_url)
        self.influence = stark_pyrust_chain.PyInfluenceClient()

        try:
            self.session_key = stark_pyrust_chain.PySessionKey()
            self.log("Session Key loaded.")
        except Exception as e:  # pragma: no cover - optional
            self.log(f"Warning: Session Key missing ({e}). Only read-ops available.")
            self.session_key = None

    def tick(self) -> None:
        try:
            block, gas_wei = self.starknet.get_network_status()
            gas_gwei = gas_wei / 1e9

            wallet = os.getenv("STARKNET_WALLET_ADDRESS")
            if wallet:
                wei = self.starknet.get_eth_balance(wallet)
                eth = wei / 1e18
                self.log(f"   Solvency: [{ 'green' if eth > 0.005 else 'red' }]{eth:.4f} ETH[/{ 'green' if eth > 0.005 else 'red' }]")
                if eth < 0.005 and not self.dry_run:
                    self.log("[bold red]⛔ Solvency Alert: Balance < 0.005 ETH. Aborting Cycle.[/bold red]")
                    return
            else:
                self.log("[yellow]⚠️  No Wallet Address. Skipping Solvency Check.[/yellow]")

            is_busy, busy_until, food_kg, location, class_id = self.influence.get_crew_metadata(1)
            status_color = "red" if is_busy else "green"
            food_color = "green" if food_kg > 550 else "red"
            class_name = "Engineer" if class_id == 1 else f"Unknown ({class_id})"
            class_color = "green" if class_id == 1 else "yellow"
            self.log(f"🔎 Scanning Adalia... [Block: {block} | Gas: {gas_gwei:.2f}] [Status: [{status_color}]{'BUSY' if is_busy else 'ACTIVE'}[/{status_color}]]")
            self.log(f"   Health: [Food: [{food_color}]{food_kg}kg[/{food_color}] | Class: [{class_color}]{class_name}[/{class_color}]]")
            if is_busy or food_kg < 550:
                return
            if class_id != 1:
                self.log("[yellow]⚠️  Efficiency Warning: Crew is not an Engineer. -50% Speed penalty active.[/yellow]")
            if gas_gwei > 30.0:
                self.log(f"[bold red]⛔ High Gas Detected ({gas_gwei:.2f} > 30.0). Yielding...[/bold red]")
                return
        except Exception as e:
            self.log(f"⚠️ Failed to fetch status: {e}")
            return

        market_prices = {
            "Iron Ore": 5.0,
            "Fuel": 2.0,
            "Steel": 20.0,
        }
        try:
            profit = self.graph.calculate_profitability("Refine Steel", market_prices)
            self.log(f"Computed Profitability: {profit:.2f} SWAY")
            if profit > 100.0:
                self.execute_refine(profit)
            else:
                self.log("Profit too low. Waiting...")
        except Exception as e:
            self.log(f"Error calculating profit: {e}")

    def execute_refine(self, profit: float) -> None:
        self.log(f"[bold green]🚀 Opportunity Detected! Profit: {profit:.2f}[/bold green]")
        payload = {
            "contract": "0xInfluenceRefinery",
            "action": "REFINE",
            "recipe": "Iron -> Steel",
            "quantity": 1,
            "timestamp": time.time(),
        }
        if self.dry_run:
            console.print(Panel(json.dumps(payload, indent=2), title="[DRY RUN] Transaction Payload"))
            self.log("Dry Run complete. No transaction sent.")
        else:
            if self.session_key:
                self.log("Transaction submitted (Mock).")
            else:
                self.log("[red]Cannot Execute: No Session Key[/red]")
