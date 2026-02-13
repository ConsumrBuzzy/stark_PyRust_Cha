"""Legacy environment loader for python-logic scripts.

Provides tolerant .env loading (UTF-8/latin-1 fallback) and alias mapping
so older scripts can share configuration without duplicating logic.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


def _parse_env_lines(lines: Iterable[str]) -> None:
    """Parse key=value lines and set env vars if not already present."""
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        # Strip inline comment after value
        if " #" in val:
            val = val.split(" #", 1)[0].strip()
        if key and key not in os.environ:
            os.environ[key] = val


def load_env_manual(env_path: str | Path = ".env") -> None:
    """Load environment variables from a .env file with encoding fallbacks and alias mapping."""
    path = Path(env_path)
    if not path.exists():
        return

    # Try UTF-8 then latin-1 fallback
    for encoding in ("utf-8", "latin-1"):
        try:
            with path.open("r", encoding=encoding) as fh:
                _parse_env_lines(fh)
            break
        except UnicodeDecodeError:
            continue
        except Exception:
            break

    # Alias mapping for legacy keys
    if "STARKNET_RPC_URL" not in os.environ:
        for alias in (
            "STARKNET_MAINNET_URL",
            "STARKNET_LAVA_URL",
            "STARKNET_1RPC_URL",
            "ANKR_ENDPOINT",
        ):
            if os.environ.get(alias):
                os.environ["STARKNET_RPC_URL"] = os.environ[alias]
                break

    if "STARKNET_PRIVATE_KEY" not in os.environ:
        for alias in ("PRIVATE_KEY", "SOLANA_PRIVATE_KEY"):
            if os.environ.get(alias):
                os.environ["STARKNET_PRIVATE_KEY"] = os.environ[alias]
                break
