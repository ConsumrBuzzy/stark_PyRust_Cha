#!/usr/bin/env python3
"""
Test suite for inventory_heartbeat.py
Ensures financial data integrity and provider reliability
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime

from inventory_heartbeat import (
    AssetBalance, ChainStatus, AssetType, PortfolioSummary,
    SolanaProvider, BaseProvider, StarknetProvider, EcosystemMonitor
)

class TestAssetBalance:
    """Test asset balance data structures"""
    
    def test_asset_balance_creation(self):
        balance = AssetBalance(
            chain="Solana",
            asset="SOL", 
            balance=1.45,
            usd_value=210.98,
            status=ChainStatus.LIQUID,
            address="test_address",
            last_updated=datetime.now()
        )
        assert balance.chain == "Solana"
        assert balance.asset == "SOL"
        assert balance.status == ChainStatus.LIQUID

class TestPortfolioSummary:
    """Test portfolio validation and calculations"""
    
    def test_valid_portfolio_summary(self):
        summary = PortfolioSummary(
            total_usd_value=1000.0,
            liquid_usd=700.0,
            locked_usd=200.0,
            in_transit_usd=100.0
        )
        assert summary.total_usd_value == 1000.0
        assert summary.liquid_usd == 700.0
    
    def test_invalid_portfolio_summary(self):
        """Test validation catches calculation errors"""
        with pytest.raises(ValueError, match="Total doesn't match sum"):
            PortfolioSummary(
                total_usd_value=1000.0,
                liquid_usd=700.0,
                locked_usd=200.0,
                in_transit_usd=150.0  # 700+200+150 = 1050, not 1000
            )

class TestSolanaProvider:
    """Test Solana chain provider"""
    
    @pytest.mark.asyncio
    async def test_get_sol_balance(self):
        provider = SolanaProvider()
        balance = await provider.get_balance("test_address", "SOL")
        assert balance == 1.45
    
    @pytest.mark.asyncio
    async def test_get_sol_price(self):
        provider = SolanaProvider()
        price = await provider.get_usd_price("SOL")
        assert price == 145.50
    
    @pytest.mark.asyncio
    async def test_unsupported_asset(self):
        provider = SolanaProvider()
        balance = await provider.get_balance("test_address", "USDC")
        assert balance is None

class TestBaseProvider:
    """Test Base chain provider"""
    
    @pytest.mark.asyncio
    async def test_get_usdc_balance(self):
        provider = BaseProvider()
        balance = await provider.get_balance("test_address", "USDC")
        assert balance == 502.00
    
    @pytest.mark.asyncio
    async def test_get_usdc_price(self):
        provider = BaseProvider()
        price = await provider.get_usd_price("USDC")
        assert price == 1.0

class TestStarknetProvider:
    """Test Starknet chain provider"""
    
    @pytest.mark.asyncio
    async def test_get_eth_balance(self):
        provider = StarknetProvider()
        balance = await provider.get_balance("test_address", "ETH")
        assert balance == 0.009
    
    @pytest.mark.asyncio
    async def test_get_eth_price(self):
        provider = StarknetProvider()
        price = await provider.get_usd_price("ETH")
        assert price == 2250.00

class TestEcosystemMonitor:
    """Test main ecosystem orchestrator"""
    
    @pytest.fixture
    def monitor(self):
        return EcosystemMonitor()
    
    @pytest.mark.asyncio
    async def test_check_solana_asset(self, monitor):
        asset = await monitor.check_asset("Solana", "SOL")
        assert asset is not None
        assert asset.chain == "Solana"
        assert asset.asset == "SOL"
        assert asset.balance == 1.45
        assert asset.status == ChainStatus.LIQUID
    
    @pytest.mark.asyncio
    async def test_check_base_asset(self, monitor):
        asset = await monitor.check_asset("Base", "USDC")
        assert asset is not None
        assert asset.chain == "Base"
        assert asset.asset == "USDC"
        assert asset.balance == 502.00
        assert asset.status == ChainStatus.LIQUID
    
    @pytest.mark.asyncio
    async def test_check_starknet_asset(self, monitor):
        asset = await monitor.check_asset("Starknet", "ETH")
        assert asset is not None
        assert asset.chain == "Starknet"
        assert asset.asset == "ETH"
        assert asset.balance == 0.009
        assert asset.status == ChainStatus.LOCKED
    
    @pytest.mark.asyncio
    async def test_generate_portfolio_summary(self, monitor):
        summary = await monitor.generate_portfolio_summary()
        
        # Verify we have all expected assets
        asset_chains = [asset.chain for asset in summary.assets]
        assert "Solana" in asset_chains
        assert "Base" in asset_chains
        assert "Starknet" in asset_chains
        
        # Verify totals are calculated correctly
        assert summary.total_usd_value > 0
        assert summary.liquid_usd > 0
        assert summary.locked_usd > 0
        
        # Verify portfolio validation passes
        assert isinstance(summary, PortfolioSummary)
    
    def test_format_markdown_report(self, monitor):
        # Create test summary
        test_asset = AssetBalance(
            chain="Test",
            asset="TEST",
            balance=100.0,
            usd_value=100.0,
            status=ChainStatus.LIQUID,
            address="test_address",
            last_updated=datetime.now()
        )
        
        summary = PortfolioSummary(
            total_usd_value=100.0,
            liquid_usd=100.0,
            locked_usd=0.0,
            in_transit_usd=0.0,
            assets=[test_asset]
        )
        
        report = monitor.format_markdown_report(summary)
        
        # Verify report structure
        assert "# Ecosystem Heartbeat" in report
        assert "## Portfolio Summary" in report
        assert "## Asset Details" in report
        assert "| Test | TEST |" in report
        assert "$100.00" in report

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
