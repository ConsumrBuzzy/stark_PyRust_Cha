"""Portfolio monitoring helpers (extracted from tools/inventory)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from loguru import logger
from pydantic import BaseModel, Field, field_validator
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class ChainStatus(str, Enum):
    LIQUID = "🟢 Liquid"
    LOCKED = "🔒 Locked"
    IN_TRANSIT = "⌛ In-Transit"
    DORMANT = "⚪ Dormant"
    ERROR = "❌ Error"


class AssetType(str, Enum):
    SOL = "SOL"
    USDC = "USDC"
    ETH = "ETH"


@dataclass
class AssetBalance:
    chain: str
    asset: str
    balance: float
    usd_value: float
    status: ChainStatus
    address: str
    last_updated: datetime


class PortfolioSummary(BaseModel):
    total_usd_value: float = Field(ge=0)
    liquid_usd: float = Field(ge=0)
    locked_usd: float = Field(ge=0)
    in_transit_usd: float = Field(ge=0)
    assets: List[AssetBalance] = Field(default_factory=list)

    @field_validator("total_usd_value")
    @classmethod
    def validate_totals(cls, v, info):
        if "liquid_usd" in info.data and "locked_usd" in info.data and "in_transit_usd" in info.data:
            calculated = info.data["liquid_usd"] + info.data["locked_usd"] + info.data["in_transit_usd"]
            if abs(v - calculated) > 0.01:
                raise ValueError(f"Total {v} doesn't match sum of components {calculated}")
        return v


class ChainProvider:
    async def get_balance(self, address: str, asset: str) -> Optional[float]:
        raise NotImplementedError

    async def get_usd_price(self, asset: str) -> Optional[float]:
        raise NotImplementedError


class MockSolanaProvider(ChainProvider):
    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        self.rpc_url = rpc_url

    async def get_balance(self, address: str, asset: str) -> Optional[float]:
        await asyncio.sleep(0.01)
        return 1.45 if asset == AssetType.SOL else None

    async def get_usd_price(self, asset: str) -> Optional[float]:
        await asyncio.sleep(0.01)
        return 145.50 if asset == AssetType.SOL else None


class MockBaseProvider(ChainProvider):
    def __init__(self, rpc_url: str = "https://mainnet.base.org"):
        self.rpc_url = rpc_url

    async def get_balance(self, address: str, asset: str) -> Optional[float]:
        await asyncio.sleep(0.01)
        return 502.0 if asset == AssetType.USDC else None

    async def get_usd_price(self, asset: str) -> Optional[float]:
        return 1.0 if asset == AssetType.USDC else None


class MockStarknetProvider(ChainProvider):
    def __init__(self, rpc_url: str = "https://starknet-mainnet.public.blastapi.io"):
        self.rpc_url = rpc_url

    async def get_balance(self, address: str, asset: str) -> Optional[float]:
        await asyncio.sleep(0.01)
        return 0.009 if asset == AssetType.ETH else None

    async def get_usd_price(self, asset: str) -> Optional[float]:
        await asyncio.sleep(0.01)
        return 2250.0 if asset == AssetType.ETH else None


class PortfolioMonitor:
    def __init__(self):
        self.console = Console()
        self.providers: Dict[str, ChainProvider] = {
            "Solana": MockSolanaProvider(),
            "Base": MockBaseProvider(),
            "Starknet": MockStarknetProvider(),
        }
        self.addresses = {
            "Solana": "phantom_wallet_address",
            "Base": "base_wallet_address",
            "Starknet": "ready_co_address",
        }
        logger.info("Portfolio monitor initialized with mock providers")

    async def check_asset(self, chain: str, asset: str) -> Optional[AssetBalance]:
        provider = self.providers.get(chain)
        if not provider:
            logger.error("No provider for chain: {}", chain)
            return None
        try:
            balance, price = await asyncio.gather(
                provider.get_balance(self.addresses[chain], asset),
                provider.get_usd_price(asset),
            )
            if balance is None or price is None:
                return None
            usd_value = balance * price
            status = self._determine_status(chain, asset, balance)
            return AssetBalance(
                chain=chain,
                asset=asset,
                balance=balance,
                usd_value=usd_value,
                status=status,
                address=self.addresses[chain],
                last_updated=datetime.now(),
            )
        except Exception as e:
            logger.error("Error checking {} on {}: {}", asset, chain, e)
            return None

    def _determine_status(self, chain: str, asset: str, balance: float) -> ChainStatus:
        if chain == "Starknet" and asset == AssetType.ETH:
            return ChainStatus.LOCKED
        elif chain == "Base" and asset == AssetType.USDC:
            return ChainStatus.LIQUID
        elif chain == "Solana" and asset == AssetType.SOL:
            return ChainStatus.LIQUID
        else:
            return ChainStatus.LIQUID

    async def generate_portfolio_summary(self) -> PortfolioSummary:
        chain_assets = {
            "Solana": [AssetType.SOL],
            "Base": [AssetType.USDC],
            "Starknet": [AssetType.ETH],
        }
        tasks = [self.check_asset(chain, asset) for chain, assets in chain_assets.items() for asset in assets]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        assets: List[AssetBalance] = []
        for result in results:
            if isinstance(result, AssetBalance):
                assets.append(result)
            elif isinstance(result, Exception):
                logger.error("Asset check failed: {}", result)

        liquid_usd = sum(a.usd_value for a in assets if a.status == ChainStatus.LIQUID)
        locked_usd = sum(a.usd_value for a in assets if a.status == ChainStatus.LOCKED)
        in_transit_usd = sum(a.usd_value for a in assets if a.status == ChainStatus.IN_TRANSIT)
        total_usd = liquid_usd + locked_usd + in_transit_usd

        summary = PortfolioSummary(
            total_usd_value=total_usd,
            liquid_usd=liquid_usd,
            locked_usd=locked_usd,
            in_transit_usd=in_transit_usd,
            assets=assets,
        )
        logger.info("Portfolio audit complete: ${:.2f} total value", total_usd)
        return summary

    def format_markdown_report(self, summary: PortfolioSummary) -> str:
        report_lines = [
            f"# Ecosystem Heartbeat - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Portfolio Summary",
            f"- **Total Value**: ${summary.total_usd_value:,.2f}",
            f"- **Liquid Assets**: ${summary.liquid_usd:,.2f}",
            f"- **Locked Assets**: ${summary.locked_usd:,.2f}",
            f"- **In-Transit**: ${summary.in_transit_usd:,.2f}",
            "",
            "## Asset Details",
            "",
            "| Chain | Asset | Balance | USD Value | Status |",
            "|-------|-------|---------|-----------|--------|",
        ]
        for asset in summary.assets:
            report_lines.append(
                f"| {asset.chain} | {asset.asset} | {asset.balance:.4f} | ${asset.usd_value:,.2f} | {asset.status.value} |"
            )
        report_lines.extend([
            "",
            "## Strategic Notes",
            f"- **Base USDC**: ${summary.liquid_usd:,.2f} available for automation/chaser strategies",
            f"- **Solana SOL**: Active in PhantomArbiter trading liquidity",
            f"- **Starknet ETH**: Locked in Ready.co paradox case study",
            "",
            "---",
            f"*Generated by portfolio monitor*",
        ])
        return "\n".join(report_lines)

    def display_rich_report(self, summary: PortfolioSummary):
        panel_content = (
            f"Total Value: ${summary.total_usd_value:,.2f}\n"
            f"Liquid: ${summary.liquid_usd:,.2f} | "
            f"Locked: ${summary.locked_usd:,.2f} | "
            f"In-Transit: ${summary.in_transit_usd:,.2f}"
        )
        self.console.print(Panel(panel_content, title="🚀 Ecosystem Heartbeat", border_style="green"))

        table = Table(title="Asset Inventory")
        table.add_column("Chain", style="cyan")
        table.add_column("Asset", style="magenta")
        table.add_column("Balance", justify="right")
        table.add_column("USD Value", justify="right", style="green")
        table.add_column("Status", style="yellow")

        for asset in summary.assets:
            table.add_row(
                asset.chain,
                asset.asset,
                f"{asset.balance:.4f}",
                f"${asset.usd_value:,.2f}",
                asset.status.value,
            )
        self.console.print(table)


def run_portfolio():
    monitor = PortfolioMonitor()
    summary = asyncio.run(monitor.generate_portfolio_summary())
    monitor.display_rich_report(summary)
    report = monitor.format_markdown_report(summary)
    report_path = Path("ecosystem_heartbeat.md")
    report_path.write_text(report, encoding="utf-8")
    logger.info("Report saved to {}", report_path)
    print(f"\n📄 Markdown report saved to: {report_path}")


__all__ = [
    "PortfolioMonitor",
    "PortfolioSummary",
    "AssetBalance",
    "AssetType",
    "ChainStatus",
    "run_portfolio",
]
