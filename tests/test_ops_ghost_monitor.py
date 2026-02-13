import sys
import types
import asyncio
from decimal import Decimal

# Stub starknet_py modules used by ghost_monitor
if "starknet_py" not in sys.modules:
    starknet_py = types.ModuleType("starknet_py")
    hash_mod = types.ModuleType("starknet_py.hash")
    selector_mod = types.ModuleType("starknet_py.hash.selector")
    net_mod = types.ModuleType("starknet_py.net")
    client_models_mod = types.ModuleType("starknet_py.net.client_models")
    fnc_mod = types.ModuleType("starknet_py.net.full_node_client")

    def get_selector_from_name(_name: str):
        return 0

    class Call:
        def __init__(self, to_addr: int, selector: int, calldata):
            self.to_addr = to_addr
            self.selector = selector
            self.calldata = calldata

    class DummyClient:
        def __init__(self, node_url: str):
            self.node_url = node_url

        async def call_contract(self, call: Call):
            # return 1 ETH in wei
            return [int(1e18)]

    selector_mod.get_selector_from_name = get_selector_from_name
    client_models_mod.Call = Call
    fnc_mod.FullNodeClient = DummyClient

    sys.modules["starknet_py"] = starknet_py
    sys.modules["starknet_py.hash"] = hash_mod
    sys.modules["starknet_py.hash.selector"] = selector_mod
    sys.modules["starknet_py.net"] = net_mod
    sys.modules["starknet_py.net.client_models"] = client_models_mod
    sys.modules["starknet_py.net.full_node_client"] = fnc_mod

from src.ops import ghost_monitor
from src.ops.ghost_monitor import GhostSettings


def test_sweep_recommended():
    settings = GhostSettings(
        ghost_address="0x1",
        main_address="0x2",
        ghost_threshold_eth=Decimal("0.5"),
        rpc_urls=[],
        eth_contract=1,
    )
    assert ghost_monitor.sweep_recommended(Decimal("0.6"), settings) is True
    assert ghost_monitor.sweep_recommended(Decimal("0.4"), settings) is False


def test_balance_with_rotation_uses_stub_client():
    settings = GhostSettings(
        ghost_address="0x1",
        main_address="0x2",
        ghost_threshold_eth=Decimal("0.5"),
        rpc_urls=["http://fake-rpc"],
        eth_contract=1,
    )
    bal, rpc = asyncio.run(
        ghost_monitor.balance_with_rotation(
            settings.ghost_address, settings.rpc_urls, settings.eth_contract
        )
    )
    assert bal == Decimal("1")
    assert rpc == "http://fake-rpc"
