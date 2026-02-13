"""RPC routing utilities with fallback selection."""

from __future__ import annotations

import asyncio
from typing import Iterable, Optional, Tuple

from starknet_py.net.full_node_client import FullNodeClient

DEFAULT_RPC_TIMEOUT = 5


async def _is_rpc_healthy(url: str, timeout: int = DEFAULT_RPC_TIMEOUT) -> bool:
    try:
        client = FullNodeClient(node_url=url)
        await asyncio.wait_for(client.get_block_number(), timeout=timeout)
        return True
    except Exception:
        return False


async def select_starknet_client(
    rpc_urls: Iterable[str],
    timeout: int = DEFAULT_RPC_TIMEOUT,
) -> Tuple[Optional[FullNodeClient], Optional[str]]:
    for url in rpc_urls:
        if not url:
            continue
        if await _is_rpc_healthy(url, timeout=timeout):
            return FullNodeClient(node_url=url), url
    return None, None


__all__ = ["select_starknet_client"]
