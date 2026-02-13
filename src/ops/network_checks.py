"""Operational network checks wrapping NetworkOracle.

Provides reusable functions for balance queries, threshold checks, and sweep
recommendations used by CLI scripts and automation.
"""

from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Dict, Tuple

from src.foundation.network import NetworkOracle
from src.ops.env import OpsConfig, build_config


async def ensure_oracle(oracle: NetworkOracle | None = None) -> NetworkOracle:
    """Initialize and return a NetworkOracle (idempotent for callers)."""

    if oracle is None:
        oracle = NetworkOracle()
    await oracle.initialize()
    return oracle


async def get_balances(
    config: OpsConfig | None = None,
    *,
    oracle: NetworkOracle | None = None,
) -> Dict[str, Decimal]:
    """Fetch phantom + starknet balances using configured addresses."""

    cfg = config or build_config()
    oracle = await ensure_oracle(oracle)

    phantom_balance = await oracle.get_balance(cfg.phantom_address, "base")
    starknet_balance = await oracle.get_balance(cfg.starknet_address, "starknet")

    return {
        "phantom_balance": Decimal(str(phantom_balance)),
        "starknet_balance": Decimal(str(starknet_balance)),
    }


async def check_threshold(
    *,
    config: OpsConfig | None = None,
    oracle: NetworkOracle | None = None,
) -> Tuple[bool, Decimal]:
    """Return (ready, starknet_balance) based on configured threshold."""

    cfg = config or build_config()
    balances = await get_balances(cfg, oracle=oracle)
    ready = balances["starknet_balance"] >= cfg.threshold_eth
    return ready, balances["starknet_balance"]


async def phantom_sweep_recommendation(
    *,
    config: OpsConfig | None = None,
    oracle: NetworkOracle | None = None,
) -> Dict[str, Decimal | bool]:
    """Determine whether to sweep phantom balance to reach StarkNet threshold."""

    cfg = config or build_config()
    oracle = await ensure_oracle(oracle)

    phantom_balance = await oracle.get_balance(cfg.phantom_address, "base")
    starknet_balance = await oracle.get_balance(cfg.starknet_address, "starknet")

    phantom_balance = Decimal(str(phantom_balance))
    starknet_balance = Decimal(str(starknet_balance))

    sweep_amount = max(Decimal("0"), phantom_balance - cfg.gas_reserve_eth)
    needed = max(Decimal("0"), cfg.threshold_eth - starknet_balance)

    return {
        "phantom_balance": phantom_balance,
        "starknet_balance": starknet_balance,
        "sweep_amount": sweep_amount,
        "needed": needed,
        "sweep_recommended": starknet_balance < cfg.threshold_eth and sweep_amount > 0,
        "sweep_sufficient": sweep_amount >= needed if needed > 0 else True,
    }


async def get_gas_price_gwei(
    *,
    oracle: NetworkOracle | None = None,
) -> int:
    """Fetch the latest StarkNet gas price in Gwei-equivalent units."""

    oracle = await ensure_oracle(oracle)
    client = oracle.clients.get("starknet")
    if client is None:
        raise RuntimeError("StarkNet client not initialized")

    block = await client.get_block("latest")
    gas_price = getattr(block, "gas_price", 0)
    return int(gas_price)


async def gas_is_safe(
    *,
    ceiling_gwei: int,
    oracle: NetworkOracle | None = None,
) -> bool:
    price = await get_gas_price_gwei(oracle=oracle)
    return price <= ceiling_gwei


__all__ = [
    "ensure_oracle",
    "get_balances",
    "check_threshold",
    "phantom_sweep_recommendation",
    "get_gas_price_gwei",
    "gas_is_safe",
]
