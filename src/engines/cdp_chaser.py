"""CDP-based inflow chaser (USDC gasless transfer from Coinbase CDP to transit address)."""
from __future__ import annotations

import os
from typing import Optional

from rich.console import Console

console = Console()

try:
    from cdp import Wallet, Cdp
except Exception:  # pragma: no cover - optional dependency
    Wallet = None
    Cdp = None


class CdpChaserEngine:
    def __init__(self, api_key_name: str, api_key_private: str, transit_address: str):
        self.api_key_name = api_key_name
        self.api_key_private = api_key_private.replace("\\n", "\n") if api_key_private else ""
        self.transit_address = transit_address
        self._configured = False

    def configure(self) -> bool:
        if not (self.api_key_name and self.api_key_private and Cdp):
            console.print("[red]❌ CDP API credentials or cdp module missing.[/red]")
            return False
        try:
            Cdp.configure(self.api_key_name, self.api_key_private)
            self._configured = True
            return True
        except Exception as e:
            console.print(f"[red]❌ CDP Configuration Error: {e}[/red]")
            return False

    def send_usdc(self, amount: float = 15.0, network_id: str = "base-mainnet") -> Optional[str]:
        if not self._configured and not self.configure():
            return None
        if not self.transit_address:
            console.print("[red]❌ TRANSIT_EVM_ADDRESS not configured.[/red]")
            return None
        try:
            wallets = list(Wallet.list())
            wallet = next((w for w in wallets if w.network_id == network_id), None)
            if not wallet:
                console.print("[yellow]⚠ No existing Base Mainnet wallet found. Creating one...[/yellow]")
                wallet = Wallet.create(network_id=network_id)
            else:
                console.print(f"[green]✅ Reusing existing CDP Wallet: {wallet.id}[/green]")

            transfer = wallet.transfer(
                amount,
                "usdc",
                self.transit_address,
                gasless=True,
            ).wait()
            console.print(f"[bold green]✅ USDC landed on transit wallet.[/bold green]")
            console.print(f"Hash: {transfer.transaction_hash}")
            return transfer.transaction_hash
        except Exception as e:
            console.print(f"[bold red]❌ CDP Transfer Failed: {e}[/bold red]")
            return None
