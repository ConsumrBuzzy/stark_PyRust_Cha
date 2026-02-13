"""Clawback analysis helpers wrapping Bridge/Clawback systems."""

from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Dict, Any, Iterable

from src.engines.bridge_system import ClawbackSystem
from src.foundation.network import NetworkOracle
from src.foundation.security import SecurityManager
from src.ops.env import OpsConfig, build_config


async def ensure_dependencies(
    oracle: NetworkOracle | None = None,
    security: SecurityManager | None = None,
) -> tuple[NetworkOracle, SecurityManager]:
    if oracle is None:
        oracle = NetworkOracle()
    await oracle.initialize()

    security = security or SecurityManager()
    return oracle, security


async def analyze_withdrawal_scenarios(
    scenarios: Iterable[tuple[str, Decimal]],
    *,
    config: OpsConfig | None = None,
    oracle: NetworkOracle | None = None,
    security: SecurityManager | None = None,
) -> Dict[str, Dict[str, Any]]:
    cfg = config or build_config()
    oracle, security = await ensure_dependencies(oracle, security)
    clawback_system = ClawbackSystem(oracle, security)

    results: Dict[str, Dict[str, Any]] = {}
    for name, amount in scenarios:
        result = await clawback_system.calculate_withdrawal_cost(amount)
        # Enrich with scenario metadata
        result["scenario"] = name
        results[name] = result
    return results


async def analyze_current_positions(
    *,
    config: OpsConfig | None = None,
    oracle: NetworkOracle | None = None,
    security: SecurityManager | None = None,
) -> Dict[str, Any]:
    cfg = config or build_config()
    oracle, security = await ensure_dependencies(oracle, security)
    clawback_system = ClawbackSystem(oracle, security)

    current_balance = await oracle.get_balance(cfg.starknet_address, "starknet")
    current_balance = Decimal(str(current_balance))

    scenarios = [
        ("Current Balance", current_balance),
        ("Target Threshold", cfg.threshold_eth),
        ("Full Target", Decimal("0.0238")),
    ]

    results = await analyze_withdrawal_scenarios(
        scenarios,
        config=cfg,
        oracle=oracle,
        security=security,
    )

    return {
        "current_balance": current_balance,
        "scenarios": results,
    }


async def simple_analysis(
    *,
    config: OpsConfig | None = None,
    oracle: NetworkOracle | None = None,
    l2_withdrawal_cost_eth: Decimal = Decimal("0.0003"),
    l1_claim_cost_eth: Decimal = Decimal("0.0005"),
) -> Dict[str, Any]:
    cfg = config or build_config()
    oracle = oracle or NetworkOracle()
    await oracle.initialize()

    current_balance = await oracle.get_balance(cfg.starknet_address, "starknet")
    current_balance = Decimal(str(current_balance))

    total_cost = l2_withdrawal_cost_eth + l1_claim_cost_eth

    def scenario(amount: Decimal) -> Dict[str, Any]:
        net_amount_eth = amount - total_cost
        net_amount_usd = float(net_amount_eth) * 2200
        profitable = net_amount_eth > 0
        return {
            "amount_eth": amount,
            "net_amount_eth": net_amount_eth,
            "net_amount_usd": net_amount_usd,
            "profitable": profitable,
        }

    scenarios = {
        "Current Balance": scenario(current_balance),
        "Target Threshold": scenario(cfg.threshold_eth),
        "Full Target": scenario(Decimal("0.0238")),
    }

    current_value_usd = float(current_balance) * 2200

    return {
        "current_balance_eth": current_balance,
        "current_value_usd": current_value_usd,
        "total_cost_eth": total_cost,
        "total_cost_usd": float(total_cost) * 2200,
        "scenarios": scenarios,
    }


__all__ = [
    "analyze_withdrawal_scenarios",
    "analyze_current_positions",
    "simple_analysis",
]
