import sys
import types
from decimal import Decimal
from datetime import datetime

# Stub starknet_py modules used by audit_ops
if "starknet_py" not in sys.modules:
    starknet_py = types.ModuleType("starknet_py")
    net_mod = types.ModuleType("starknet_py.net")
    fnc_mod = types.ModuleType("starknet_py.net.full_node_client")
    selector_mod = types.ModuleType("starknet_py.hash.selector")
    client_models_mod = types.ModuleType("starknet_py.net.client_models")

    class DummyClient:
        def __init__(self, node_url: str):
            self.node_url = node_url

        async def call_contract(self, call):
            # Return 1 ETH in wei
            return [int(1e18)]

        async def get_block_number(self):
            return 1

        async def get_class_at(self, contract_address: str, block_number: str):
            return "0xclass"

    def get_selector_from_name(_name: str):
        return 0

    class Call:
        def __init__(self, to_addr: int, selector: int, calldata):
            self.to_addr = to_addr
            self.selector = selector
            self.calldata = calldata

    fnc_mod.FullNodeClient = DummyClient
    selector_mod.get_selector_from_name = get_selector_from_name
    client_models_mod.Call = Call

    sys.modules["starknet_py"] = starknet_py
    sys.modules["starknet_py.net"] = net_mod
    sys.modules["starknet_py.net.full_node_client"] = fnc_mod
    sys.modules["starknet_py.hash.selector"] = selector_mod
    sys.modules["starknet_py.net.client_models"] = client_models_mod

import os
os.environ["STARKNET_RPC_URL"] = "https://rpc"
os.environ["STARKNET_WALLET_ADDRESS"] = "0x1"
os.environ["STARKNET_GHOST_ADDRESS"] = "0x2"

from src.ops.audit_ops import run_audit, build_tables

import asyncio


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
