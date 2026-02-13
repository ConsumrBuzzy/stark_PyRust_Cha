"""Audit helpers for StarkNet balances and deployment status."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

from loguru import logger
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call

from src.ops.rpc_router import select_starknet_client

from src.ops.env import build_config, load_dotenv


@dataclass
class AuditResult:
    ghost_balance_eth: Decimal
    main_balance_eth: Decimal
    deployed: bool
    deployment_status: str
    timestamp: datetime


async def _get_eth_balance(client: FullNodeClient, address: str, eth_contract: int) -> Decimal:
    call = Call(
        to_addr=eth_contract,
        selector=get_selector_from_name("balanceOf"),
        calldata=[int(address, 16)],
    )
    result = await client.call_contract(call)
    return Decimal(result[0]) / Decimal(1e18)


async def _check_deployment(client: FullNodeClient, address: str) -> Dict[str, Any]:
    try:
        code_response = await client.get_class_at(contract_address=address, block_number="latest")
        return {"deployed": True, "class_hash": code_response, "status": "deployed"}
    except Exception as e:
        return {"deployed": False, "class_hash": None, "status": f"not_deployed: {e}"}


async def run_audit(
    *,
    ghost_address: str | None = None,
    main_address: str | None = None,
    rpc_url: str | None = None,
    eth_contract: int | None = None,
) -> AuditResult:
    load_dotenv()
    cfg = build_config()
    ghost = ghost_address or os.getenv("STARKNET_GHOST_ADDRESS") or cfg.phantom_address
    main = main_address or cfg.starknet_address
    rpc_candidates = [
        rpc_url,
        os.getenv("STARKNET_MAINNET_URL"),  # prefer mainnet (Alchemy/primary)
        os.getenv("STARKNET_RPC_URL"),
        os.getenv("STARKNET_LAVA_URL"),
        os.getenv("STARKNET_1RPC_URL"),
        os.getenv("STARKNET_ONFINALITY_URL"),
        "https://starknet-mainnet.public.blastapi.io",
        "https://1rpc.io/starknet",
        "https://starknet.api.onfinality.io/public",
    ]

    rpc = next((u for u in rpc_candidates if u), None)
    eth = eth_contract or int(
        os.getenv(
            "STARKNET_ETH_CONTRACT",
            "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
        ),
        16,
    )

    if not rpc:
        raise ValueError("No RPC URL configured")

    client, selected_rpc = await select_starknet_client(rpc_candidates)
    if client is None:
        raise ValueError("No healthy StarkNet RPC available")

    ghost_bal, main_bal, deployment = await asyncio.gather(
        _get_eth_balance(client, ghost, eth),
        _get_eth_balance(client, main, eth),
        _check_deployment(client, main),
    )

    return AuditResult(
        ghost_balance_eth=ghost_bal,
        main_balance_eth=main_bal,
        deployed=deployment.get("deployed", False),
        deployment_status=deployment.get("status", "unknown"),
        timestamp=datetime.now(),
    )


def build_tables(result: AuditResult) -> tuple[Table, Panel]:
    table = Table(title="Address Balance Check")
    table.add_column("Address", style="cyan")
    table.add_column("Label", style="magenta")
    table.add_column("ETH Balance", justify="right", style="green")
    table.add_column("Status", style="yellow")

    table.add_row("Ghost", "Ghost Address", f"{result.ghost_balance_eth:.6f}", "OK")
    table.add_row("Main", "Main Wallet", f"{result.main_balance_eth:.6f}", result.deployment_status)

    status_text = "✅ DEPLOYED" if result.deployed else "❌ NOT DEPLOYED"
    deployment_panel = Panel(
        f"Main Wallet Status: {status_text}\nDeployment: {result.deployment_status}\nTimestamp: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        title="🚀 Deployment Status",
        border_style="green" if result.deployed else "red",
    )
    return table, deployment_panel


def display_results(result: AuditResult):
    console = Console()
    table, deployment_panel = build_tables(result)
    console.print(table)
    console.print(deployment_panel)


__all__ = ["run_audit", "display_results", "AuditResult"]
