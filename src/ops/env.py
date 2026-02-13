"""Environment helpers and shared operational constants.

Centralizes .env loading and default addresses/thresholds used by CLI scripts.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Optional

from src.foundation import constants as foundation_constants

# Default addresses used across scripts (can be overridden via environment)
DEFAULT_STARKNET_ADDRESS = "0x05174a29cc99c36c124c85e17fab10c12c3a783e64f46c29f107b316ec4853a9"
DEFAULT_PHANTOM_ADDRESS = "0xbd5fdCDc18FA0B0764861996CC9482f0526EEDd9"

# Thresholds and operational tunables (override via env if present)
DEFAULT_THRESHOLD = Decimal(str(getattr(foundation_constants, "ACTIVATION_THRESHOLD", 0.018)))
DEFAULT_GAS_RESERVE = Decimal(str(getattr(foundation_constants, "GAS_RESERVE", 0.001)))
DEFAULT_GAS_CEILING_GWEI = int(os.getenv("GAS_CEILING_GWEI", "100"))


@dataclass(frozen=True)
class OpsConfig:
    starknet_address: str = DEFAULT_STARKNET_ADDRESS
    phantom_address: str = DEFAULT_PHANTOM_ADDRESS
    threshold_eth: Decimal = DEFAULT_THRESHOLD
    gas_reserve_eth: Decimal = DEFAULT_GAS_RESERVE
    gas_ceiling_gwei: int = DEFAULT_GAS_CEILING_GWEI


def load_dotenv(dotenv_path: Path | str = Path(".env")) -> None:
    """Minimal .env loader to populate os.environ.

    This mirrors the ad-hoc loaders used in scripts but consolidates them for reuse.
    """

    path = Path(dotenv_path)
    if not path.exists():
        return

    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if "=" not in line or line.strip().startswith("#"):
                continue
            key, value = line.strip().split("=", 1)
            os.environ[key] = value


def build_config(
    *,
    starknet_address: Optional[str] = None,
    phantom_address: Optional[str] = None,
    threshold_eth: Optional[Decimal] = None,
    gas_reserve_eth: Optional[Decimal] = None,
    gas_ceiling_gwei: Optional[int] = None,
) -> OpsConfig:
    """Create an OpsConfig with env overrides and optional explicit overrides."""

    load_dotenv()

    return OpsConfig(
        starknet_address=starknet_address
        or os.getenv("STARKNET_WALLET_ADDRESS")
        or DEFAULT_STARKNET_ADDRESS,
        phantom_address=phantom_address
        or os.getenv("PHANTOM_BASE_ADDRESS")
        or DEFAULT_PHANTOM_ADDRESS,
        threshold_eth=threshold_eth
        or Decimal(os.getenv("ACTIVATION_THRESHOLD", str(DEFAULT_THRESHOLD))),
        gas_reserve_eth=gas_reserve_eth
        or Decimal(os.getenv("GAS_RESERVE", str(DEFAULT_GAS_RESERVE))),
        gas_ceiling_gwei=gas_ceiling_gwei
        or int(os.getenv("GAS_CEILING_GWEI", str(DEFAULT_GAS_CEILING_GWEI))),
    )
