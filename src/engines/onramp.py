"""Onramp engine for Coinbase -> Base (transit) flow using CCXT/CDP credentials."""
from __future__ import annotations

import os
from typing import Optional
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel

try:  # ccxt is optional dependency
    import ccxt.async_support as ccxt
except Exception:  # pragma: no cover
    ccxt = None

console = Console()


@dataclass
class OnrampResult:
    success: bool
    message: str
    withdrawal_id: Optional[str] = None
    amount_eth: Optional[float] = None
    network: str = "base"
    dry_run: bool = False


class CoinbaseOnrampEngine:
    ALLOWED_NETWORK = "base"

    def __init__(self, transit_address: str, api_key_name: str, api_private_key: str, dry_run: bool = True):
        self.transit_address = transit_address
        self.api_key_name = api_key_name
        self.api_private_key = api_private_key.replace("\\n", "\n") if api_private_key else ""
        self.dry_run = dry_run
        self._exchange = None

    async def _ensure_exchange(self):
        if self._exchange is None and ccxt:
            self._exchange = ccxt.coinbase({
                "apiKey": self.api_key_name,
                "secret": self.api_private_key,
                "verbose": False,
                "enableRateLimit": True,
                "options": {
                    "defaultType": "spot",
                    "brokerId": "CCXT",
                },
            })
        return self._exchange

    async def close(self):
        if self._exchange:
            await self._exchange.close()

    async def get_balance(self, asset: str = "ETH") -> float:
        try:
            exchange = await self._ensure_exchange()
            if not exchange:
                return 0.0
            balance = await exchange.fetch_balance()
            asset_bal = balance.get(asset, {})
            return float(asset_bal.get("free", 0.0))
        except Exception as e:
            console.print(f"[red]❌ Balance fetch error: {e}[/red]")
            return 0.0

    async def bridge_funds(self, min_gas_buffer: float = 0.0005, target_amount: float = 0.005) -> OnrampResult:
        if not self.transit_address:
            return OnrampResult(False, "TRANSIT_EVM_ADDRESS not configured")
        if not self.api_key_name or not self.api_private_key:
            return OnrampResult(False, "Coinbase CDP credentials not configured")

        eth_bal = await self.get_balance("ETH")
        if eth_bal < target_amount:
            return OnrampResult(False, f"Insufficient ETH on Coinbase ({eth_bal:.4f})", amount_eth=eth_bal)

        amount = eth_bal - min_gas_buffer

        if self.dry_run:
            return OnrampResult(True, "Dry run", amount_eth=amount, dry_run=True)

        try:
            exchange = await self._ensure_exchange()
            if not exchange:
                return OnrampResult(False, "Exchange client not available")

            params = {"network": self.ALLOWED_NETWORK}
            withdrawal = await exchange.withdraw(
                code="ETH",
                amount=amount,
                address=self.transit_address,
                params=params,
            )
            return OnrampResult(True, "Withdrawal initialized", withdrawal_id=str(withdrawal.get("id")), amount_eth=amount)
        except Exception as e:
            return OnrampResult(False, f"Withdrawal failed: {e}")
