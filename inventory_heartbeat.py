#!/usr/bin/env python3
"""
Multi-chain Asset Inventory & Monitoring System
Tracks liquid and illiquid assets across Solana, Base, and Starknet ecosystems
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pydantic import BaseModel, Field, validator

# Load environment variables
load_dotenv()

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

    @validator('total_usd_value')
    def validate_totals(cls, v, values):
        calculated = (
            values.get('liquid_usd', 0) + 
            values.get('locked_usd', 0) + 
            values.get('in_transit_usd', 0)
        )
        if abs(v - calculated) > 0.01:  # Allow $0.01 rounding
            raise ValueError(f"Total {v} doesn't match sum of components {calculated}")
        return v

class ChainProvider:
    """Abstract base class for chain-specific providers"""
    
    async def get_balance(self, address: str, asset: str) -> Optional[float]:
        raise NotImplementedError
    
    async def get_usd_price(self, asset: str) -> Optional[float]:
        raise NotImplementedError

class SolanaProvider(ChainProvider):
    """Solana chain interactions via Phantom wallet"""
    
    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        self.rpc_url = rpc_url
        # Note: In production, use actual Solana-Py client
        logger.info("Solana provider initialized")
    
    async def get_balance(self, address: str, asset: str) -> Optional[float]:
        """Mock implementation - replace with actual Solana-Py RPC calls"""
        await asyncio.sleep(0.1)  # Simulate network latency
        
        if asset == AssetType.SOL:
            # Mock balance from your inventory
            return 1.45
        return None
    
    async def get_usd_price(self, asset: str) -> Optional[float]:
        """Mock SOL price - replace with CoinGecko/Jupiter API"""
        await asyncio.sleep(0.05)
        if asset == AssetType.SOL:
            return 145.50  # Mock price
        return None

class BaseProvider(ChainProvider):
    """Base chain interactions via EVM"""
    
    def __init__(self, rpc_url: str = "https://mainnet.base.org"):
        self.rpc_url = rpc_url
        logger.info("Base provider initialized")
    
    async def get_balance(self, address: str, asset: str) -> Optional[float]:
        """Mock implementation - replace with Web3.py calls"""
        await asyncio.sleep(0.1)
        
        if asset == AssetType.USDC:
            # Mock balance from your inventory
            return 502.00
        return None
    
    async def get_usd_price(self, asset: str) -> Optional[float]:
        """USDC is pegged to USD"""
        return 1.0

class StarknetProvider(ChainProvider):
    """Starknet chain interactions via Ready.co"""
    
    def __init__(self, rpc_url: str = "https://starknet-mainnet.public.blastapi.io"):
        self.rpc_url = rpc_url
        logger.info("Starknet provider initialized")
    
    async def get_balance(self, address: str, asset: str) -> Optional[float]:
        """Mock implementation - replace with Starknet.py calls"""
        await asyncio.sleep(0.1)
        
        if asset == AssetType.ETH:
            # Mock balance from your inventory
            return 0.009
        return None
    
    async def get_usd_price(self, asset: str) -> Optional[float]:
        """Mock ETH price - replace with CoinGecko API"""
        await asyncio.sleep(0.05)
        if asset == AssetType.ETH:
            return 2250.00  # Mock price
        return None

class EcosystemMonitor:
    """Main orchestrator for multi-chain asset monitoring"""
    
    def __init__(self):
        self.console = Console()
        self.providers = {
            "Solana": SolanaProvider(),
            "Base": BaseProvider(), 
            "Starknet": StarknetProvider(),
        }
        self.addresses = {
            "Solana": os.getenv("SOLANA_ADDRESS", "phantom_wallet_address"),
            "Base": os.getenv("BASE_ADDRESS", "base_wallet_address"),
            "Starknet": os.getenv("STARKNET_ADDRESS", "ready_co_address"),
        }
        logger.info("Ecosystem monitor initialized with {} providers", len(self.providers))
    
    async def check_asset(self, chain: str, asset: str) -> Optional[AssetBalance]:
        """Check single asset balance across a specific chain"""
        provider = self.providers.get(chain)
        if not provider:
            logger.error("No provider found for chain: {}", chain)
            return None
        
        try:
            balance, price = await asyncio.gather(
                provider.get_balance(self.addresses[chain], asset),
                provider.get_usd_price(asset)
            )
            
            if balance is None or price is None:
                logger.warning("Failed to get balance or price for {} on {}", asset, chain)
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
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error("Error checking {} on {}: {}", asset, chain, e)
            return None
    
    def _determine_status(self, chain: str, asset: str, balance: float) -> ChainStatus:
        """Determine asset status based on chain and balance"""
        if chain == "Starknet" and asset == AssetType.ETH:
            return ChainStatus.LOCKED  # Ready.co paradox
        elif chain == "Base" and asset == AssetType.USDC:
            return ChainStatus.LIQUID  # Primary chaser capital
        elif chain == "Solana" and asset == AssetType.SOL:
            return ChainStatus.LIQUID  # PhantomArbiter liquidity
        else:
            return ChainStatus.LIQUID
    
    async def generate_portfolio_summary(self) -> PortfolioSummary:
        """Generate complete portfolio summary across all chains"""
        logger.info("Starting portfolio audit...")
        
        # Define assets to check per chain
        chain_assets = {
            "Solana": [AssetType.SOL],
            "Base": [AssetType.USDC],
            "Starknet": [AssetType.ETH],
        }
        
        # Check all assets concurrently
        tasks = []
        for chain, assets in chain_assets.items():
            for asset in assets:
                tasks.append(self.check_asset(chain, asset))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        assets = []
        for result in results:
            if isinstance(result, AssetBalance):
                assets.append(result)
            elif isinstance(result, Exception):
                logger.error("Asset check failed: {}", result)
        
        # Calculate totals
        liquid_usd = sum(a.usd_value for a in assets if a.status == ChainStatus.LIQUID)
        locked_usd = sum(a.usd_value for a in assets if a.status == ChainStatus.LOCKED)
        in_transit_usd = sum(a.usd_value for a in assets if a.status == ChainStatus.IN_TRANSIT)
        total_usd = liquid_usd + locked_usd + in_transit_usd
        
        summary = PortfolioSummary(
            total_usd_value=total_usd,
            liquid_usd=liquid_usd,
            locked_usd=locked_usd,
            in_transit_usd=in_transit_usd,
            assets=assets
        )
        
        logger.info("Portfolio audit complete: ${:.2f} total value", total_usd)
        return summary
    
    def format_markdown_report(self, summary: PortfolioSummary) -> str:
        """Generate clean markdown report for user consumption"""
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
                f"| {asset.chain} | {asset.asset} | {asset.balance:.4f} | "
                f"${asset.usd_value:,.2f} | {asset.status.value} |"
            )
        
        report_lines.extend([
            "",
            "## Strategic Notes",
            f"- **Base USDC**: ${summary.liquid_usd:,.2f} available for automation/chaser strategies",
            f"- **Solana SOL**: Active in PhantomArbiter trading liquidity",
            f"- **Starknet ETH**: Locked in Ready.co paradox case study",
            "",
            "---",
            f"*Generated by inventory_heartbeat.py*"
        ])
        
        return "\n".join(report_lines)
    
    def display_rich_report(self, summary: PortfolioSummary):
        """Display formatted report in terminal using Rich"""
        # Portfolio summary panel
        panel_content = (
            f"Total Value: ${summary.total_usd_value:,.2f}\n"
            f"Liquid: ${summary.liquid_usd:,.2f} | "
            f"Locked: ${summary.locked_usd:,.2f} | "
            f"In-Transit: ${summary.in_transit_usd:,.2f}"
        )
        
        self.console.print(Panel(
            panel_content,
            title="🚀 Ecosystem Heartbeat",
            border_style="green"
        ))
        
        # Assets table
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
                asset.status.value
            )
        
        self.console.print(table)
        
        # Strategic notes
        notes = [
            f"🎯 Base USDC: ${summary.liquid_usd:,.2f} ready for automation strategies",
            f"⚡ Solana SOL: Active trading liquidity",
            f"🔒 Starknet ETH: Ready.co case study"
        ]
        
        for note in notes:
            self.console.print(f"  {note}")

async def main():
    """Main execution entry point"""
    logger.info("Starting ecosystem heartbeat...")
    
    monitor = EcosystemMonitor()
    summary = await monitor.generate_portfolio_summary()
    
    # Display in terminal
    monitor.display_rich_report(summary)
    
    # Save markdown report
    report = monitor.format_markdown_report(summary)
    report_path = Path("ecosystem_heartbeat.md")
    
    with open(report_path, "w") as f:
        f.write(report)
    
    logger.info("Report saved to {}", report_path)
    print(f"\n📄 Markdown report saved to: {report_path}")

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Run the monitor
    asyncio.run(main())
