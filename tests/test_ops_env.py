import os
from decimal import Decimal

from src.ops import env


def test_build_config_defaults(monkeypatch):
    monkeypatch.delenv("STARKNET_WALLET_ADDRESS", raising=False)
    monkeypatch.delenv("PHANTOM_BASE_ADDRESS", raising=False)
    cfg = env.build_config()
    assert cfg.threshold_eth == Decimal(str(env.DEFAULT_THRESHOLD))
    assert cfg.gas_reserve_eth == Decimal(str(env.DEFAULT_GAS_RESERVE))
    assert cfg.starknet_address == env.DEFAULT_STARKNET_ADDRESS
    assert cfg.phantom_address == env.DEFAULT_PHANTOM_ADDRESS


def test_build_config_overrides(monkeypatch):
    # Prevent reading real .env so env overrides take effect
    monkeypatch.setattr(env, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setenv("STARKNET_WALLET_ADDRESS", "0xabc")
    monkeypatch.setenv("PHANTOM_BASE_ADDRESS", "0xdef")
    monkeypatch.setenv("ACTIVATION_THRESHOLD", "0.123")
    monkeypatch.setenv("GAS_RESERVE", "0.002")
    monkeypatch.setenv("GAS_CEILING_GWEI", "77")

    cfg = env.build_config()
    assert cfg.starknet_address == "0xabc"
    assert cfg.phantom_address == "0xdef"
    assert cfg.threshold_eth == Decimal("0.123")
    assert cfg.gas_reserve_eth == Decimal("0.002")
    assert cfg.gas_ceiling_gwei == 77
