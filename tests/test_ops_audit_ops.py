import os
import sys
import types
import asyncio
from decimal import Decimal

import src.ops.audit_ops as audit_ops


class DummyClient:
    def __init__(self, node_url: str):
        self.node_url = node_url

    async def call_contract(self, call):
        return [int(1e18)]

    async def get_class_at(self, contract_address: str, block_number: str):
        return "0xclass"


# Stub starknet_py selector/Call modules so audit_ops imports succeed
if "starknet_py.hash.selector" not in sys.modules:
    selector_mod = types.ModuleType("starknet_py.hash.selector")

    def get_selector_from_name(_name: str):
        return 0

    selector_mod.get_selector_from_name = get_selector_from_name
    sys.modules["starknet_py.hash.selector"] = selector_mod

if "starknet_py.net.client_models" not in sys.modules:
    client_models_mod = types.ModuleType("starknet_py.net.client_models")

    class Call:
        def __init__(self, to_addr: int, selector: int, calldata):
            self.to_addr = to_addr
            self.selector = selector
            self.calldata = calldata

    client_models_mod.Call = Call
    sys.modules["starknet_py.net.client_models"] = client_models_mod

# Monkeypatch audit_ops loader to use DummyClient
audit_ops._load_client = lambda rpc_url: DummyClient(rpc_url)  # type: ignore

os.environ["STARKNET_RPC_URL"] = "https://rpc"
os.environ["STARKNET_WALLET_ADDRESS"] = "0x1"
os.environ["STARKNET_GHOST_ADDRESS"] = "0x2"


from src.ops.audit_ops import run_audit, build_tables


def test_run_audit_returns_balances():
    result = asyncio.run(run_audit())
    assert result.ghost_balance_eth == Decimal(1)
    assert result.main_balance_eth == Decimal(1)
    assert result.deployed is True


def test_build_tables_returns_table_panel():
    from rich.table import Table
    from rich.panel import Panel

    result = asyncio.run(run_audit())
    table, panel = build_tables(result)
    assert isinstance(table, Table)
    assert isinstance(panel, Panel)
