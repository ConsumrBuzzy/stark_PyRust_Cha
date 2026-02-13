"""Ghost monitoring and recovery helpers."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Optional, Tuple

from starknet_py.net.client_models import Call
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.full_node_client import FullNodeClient

from src.ops.env import build_config, load_dotenv
from src.ops.network_checks import ensure_oracle


@dataclass
class GhostSettings:
    ghost_address: str
    main_address: str
    ghost_threshold_eth: Decimal
    rpc_urls: list[str]
    eth_contract: int


DEFAULT_ETH_CONTRACT = int(
    os.getenv(
        "STARKNET_ETH_CONTRACT",
        "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
    ),
    16,
)


def load_settings() -> GhostSettings:
    load_dotenv()
    cfg = build_config()
    ghost_address = os.getenv("STARKNET_GHOST_ADDRESS") or cfg.phantom_address
    main_address = cfg.starknet_address
    ghost_threshold = Decimal(os.getenv("GHOST_THRESHOLD", "0.005"))
    rpc_urls = [
        url
        for url in [
            os.getenv("STARKNET_MAINNET_URL"),
            os.getenv("STARKNET_LAVA_URL"),
            os.getenv("STARKNET_1RPC_URL"),
            os.getenv("STARKNET_ONFINALITY_URL"),
        ]
        if url
    ]
    return GhostSettings(
        ghost_address=ghost_address,
        main_address=main_address,
        ghost_threshold_eth=ghost_threshold,
        rpc_urls=rpc_urls,
        eth_contract=DEFAULT_ETH_CONTRACT,
    )


async def starknet_eth_balance(
    address: str,
    *,
    oracle=None,
) -> Decimal:
    """Get ETH balance on StarkNet using NetworkOracle if available."""

    o = await ensure_oracle(oracle)
    bal = await o.get_balance(address, "starknet")
    return Decimal(str(bal))


async def balance_via_rpc(address: str, rpc_url: str, eth_contract: int) -> Decimal:
    client = FullNodeClient(node_url=rpc_url)
    call = Call(
        to_addr=eth_contract,
        selector=get_selector_from_name("balanceOf"),
        calldata=[int(address, 16)],
    )
    result = await client.call_contract(call)
    return Decimal(result[0]) / Decimal(1e18)


async def balance_with_rotation(
    address: str,
    rpc_urls: Iterable[str],
    eth_contract: int,
) -> Tuple[Optional[Decimal], Optional[str]]:
    for url in rpc_urls:
        try:
            bal = await balance_via_rpc(address, url, eth_contract)
            return bal, url
        except Exception:
            continue
    return None, None


async def check_ghost_balance(
    settings: Optional[GhostSettings] = None,
    *,
    use_rpc_rotation: bool = False,
) -> Tuple[Decimal, Optional[str]]:
    settings = settings or load_settings()
    if use_rpc_rotation and settings.rpc_urls:
        bal, rpc = await balance_with_rotation(
            settings.ghost_address, settings.rpc_urls, settings.eth_contract
        )
        return bal or Decimal("0"), rpc
    # fallback to oracle
    bal = await starknet_eth_balance(settings.ghost_address)
    return bal, None


def sweep_recommended(balance: Decimal, settings: Optional[GhostSettings] = None) -> bool:
    settings = settings or load_settings()
    return balance >= settings.ghost_threshold_eth


__all__ = [
    "GhostSettings",
    "load_settings",
    "starknet_eth_balance",
    "balance_with_rotation",
    "check_ghost_balance",
    "sweep_recommended",
]
