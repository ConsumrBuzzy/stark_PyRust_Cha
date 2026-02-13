"""
Orbiter Bridge Logic (Base -> Starknet)
=======================================
Implements ADR-047: Hybrid Bridge.
Moves ETH from Base (L2) to Starknet via Orbiter Finance.
"""

import os
import sys
import json
import asyncio
from decimal import Decimal
from rich.console import Console
from rich.panel import Panel
from pathlib import Path

# Add src to path for shared legacy env loader
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from foundation.legacy_env import load_env_manual
    from foundation.security import SecurityManager
    from foundation.constants import BASE_RPC_URL
    from engines.bridge_system import OrbiterBridgeAdapter
except Exception:
    def load_env_manual():  # type: ignore
        return
    SecurityManager = None
    OrbiterBridgeAdapter = None
    BASE_RPC_URL = "https://mainnet.base.org"

try:
    from web3 import Web3
except ImportError:
    print("Error: web3 not installed. Run 'pip install web3'")
    sys.exit(1)

console = Console()
load_env_manual()

# Orbiter Makers (Check https://github.com/Orbiter-Finance/Orbiter-Bridge-Contracts)
# Base (Chain 8453) -> Starknet (9004)
# Maker Address usually stable, but verify if fails.
ORBITER_MAKER_BASE = "0xe530d28960d48708ccf3e62aa7b42a80bc427aef" 
STARKNET_CODE = 9004

class OrbiterBridge:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
        self.security_manager = SecurityManager() if SecurityManager else None
        
        # Load Transit Key
        self.private_key = os.getenv("TRANSIT_EVM_PRIVATE_KEY")
        if not self.private_key:
            console.print("[red]❌ TRANSIT_EVM_PRIVATE_KEY not found in .env[/red]")
            self.account = None
            return

        try:
            self.account = self.w3.eth.account.from_key(self.private_key)
            console.print(f"[green]✅ Transit Wallet Loaded:[/green] {self.account.address}")
        except Exception as e:
            console.print(f"[red]❌ Invalid EVM Key:[/red] {e}")
            self.account = None

        # Adapter for Orbiter path
        self.adapter = OrbiterBridgeAdapter(
            base_web3=self.w3,
            security_manager=self.security_manager,
            maker_address=ORBITER_MAKER_BASE,
            destination_code=STARKNET_CODE,
            min_amount_eth=0.005,
        ) if OrbiterBridgeAdapter else None

    def get_balance(self):
        if not self.account: return 0.0
        return asyncio.run(self.adapter.get_balance(self.account.address)) if self.adapter else 0.0

    def bridge_to_starknet(self, amount_eth):
        """
        Sends ETH to Orbiter Maker with the 9004 code.
        """
        if not self.account or not self.adapter:
            return

        console.print(Panel.fit("[bold blue]🌉 Base -> Starknet (via Orbiter)[/bold blue]"))
        
        balance = asyncio.run(self.adapter.get_balance(self.account.address))
        console.print(f"   💰 Transit Balance (Base): {balance:.4f} ETH")

        if balance < amount_eth:
            console.print(f"[red]⛔ Insufficient Balance on Base. Need {amount_eth} ETH.[/red]")
            return

        if amount_eth < self.adapter.min_amount_eth:
            console.print(f"[red]⛔ Amount too low for Orbiter (Min ~{self.adapter.min_amount_eth} ETH).[/red]")
            return

        result = asyncio.run(self.adapter.bridge_to_starknet(
            amount_eth=amount_eth,
            transit_address=self.account.address,
            dry_run=self.dry_run,
            override_key=self.private_key,
        ))

        if result.get("dry_run"):
            payload = result["payload"]
            console.print(Panel(
                f"[DRY RUN] Transaction Payload:\n"
                f"To: {payload['to']}\n"
                f"Value: {payload['value']} wei\n"
                f"ChainId: {payload['chainId']} (Base)\n"
                f"Nonce: {payload['nonce']}",
                title="Simulation"
            ))
            return

        if result.get("success"):
            console.print("[yellow]🚀 Broadcasting to Base Network...[/yellow]")
            console.print(f"[green]✅ Bridge Tx Sent! Hash: {result['tx_hash']}[/green]")
            console.print("[dim]Wait ~2 mins for funds to arrive on Starknet.[/dim]")
        else:
            console.print(f"[bold red]❌ Bridge Failed: {result.get('error')}[/bold red]")

if __name__ == "__main__":
    is_dry = "--no-dry-run" not in sys.argv
    bridge = OrbiterBridge(dry_run=is_dry)
    # Default behavior: Bridge ALL available ETH minus gas
    bal = bridge.get_balance()
    if bal > 0.002:
        bridge.bridge_to_starknet(bal - 0.0005) # Leave small gas for Base execution
    else:
        console.print("[yellow]Transit wallet empty or below min threshold.[/yellow]")
