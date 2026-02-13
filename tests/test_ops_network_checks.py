import asyncio
from decimal import Decimal

import pytest

from src.ops import network_checks
from src.ops.env import OpsConfig


class DummyClient:
    def __init__(self, gas_price: int = 42):
        self.gas_price = gas_price

    async def get_block(self, _latest):
        return self


class DummyOracle:
    def __init__(self, phantom_balance: Decimal, starknet_balance: Decimal, gas_price: int = 42):
        self._phantom = phantom_balance
        self._starknet = starknet_balance
        self.clients = {"starknet": DummyClient(gas_price)}
        self._initialized = False

    async def initialize(self):
        self._initialized = True

    async def get_balance(self, address: str, network: str):
        return self._phantom if network == "base" else self._starknet


@pytest.mark.asyncio
async def test_check_threshold_ready():
    cfg = OpsConfig(threshold_eth=Decimal("0.01"))
    oracle = DummyOracle(Decimal("0.001"), Decimal("0.02"))
    ready, balance = await network_checks.check_threshold(config=cfg, oracle=oracle)
    assert ready is True
    assert balance == Decimal("0.02")


@pytest.mark.asyncio
async def test_phantom_sweep_recommendation_insufficient():
    cfg = OpsConfig(threshold_eth=Decimal("0.02"), gas_reserve_eth=Decimal("0.002"))
    oracle = DummyOracle(Decimal("0.002"), Decimal("0.01"))
    result = await network_checks.phantom_sweep_recommendation(config=cfg, oracle=oracle)
    assert result["sweep_recommended"] is False
    assert result["sweep_amount"] == Decimal("0")


@pytest.mark.asyncio
async def test_get_gas_price_gwei():
    oracle = DummyOracle(Decimal("0"), Decimal("0"), gas_price=55)
    price = await network_checks.get_gas_price_gwei(oracle=oracle)
    assert price == 55
