import asyncio
import sys
import types
from decimal import Decimal


# Stub minimal web3 modules to satisfy src.foundation.network imports
if "web3" not in sys.modules:
    web3_stub = types.ModuleType("web3")
    middleware_stub = types.ModuleType("web3.middleware")

    class DummyHTTPProvider:
        def __init__(self, _url):
            pass

    class DummyMiddlewareOnion:
        def inject(self, *_args, **_kwargs):
            return None

    class DummyEth:
        def __init__(self):
            self.block_number = 0

        def get_balance(self, _addr):
            return 0

    class DummyWeb3:
        def __init__(self, *_args, **_kwargs):
            self.middleware_onion = DummyMiddlewareOnion()
            self.eth = DummyEth()

        def from_wei(self, value, _unit):
            return value

    web3_stub.Web3 = DummyWeb3
    web3_stub.HTTPProvider = DummyHTTPProvider
    middleware_stub.ExtraDataToPOAMiddleware = object

    sys.modules["web3"] = web3_stub
    sys.modules["web3.middleware"] = middleware_stub

# Stub minimal starknet_py modules used by foundation.network
if "starknet_py" not in sys.modules:
    starknet_py = types.ModuleType("starknet_py")
    net_mod = types.ModuleType("starknet_py.net")
    fnc_mod = types.ModuleType("starknet_py.net.full_node_client")
    selector_mod = types.ModuleType("starknet_py.hash.selector")
    client_models_mod = types.ModuleType("starknet_py.net.client_models")

    class DummyFullNodeClient:
        def __init__(self, node_url: str):
            self.node_url = node_url

        async def get_block_number(self):
            return 0

        async def get_block(self, _latest):
            return types.SimpleNamespace(gas_price=20)

        async def call_contract(self, _call):
            return [0]

    def get_selector_from_name(_name: str):
        return 0

    class Call:
        def __init__(self, to_addr: int, selector: int, calldata):
            self.to_addr = to_addr
            self.selector = selector
            self.calldata = calldata

    fnc_mod.FullNodeClient = DummyFullNodeClient
    selector_mod.get_selector_from_name = get_selector_from_name
    client_models_mod.Call = Call

    sys.modules["starknet_py"] = starknet_py
    sys.modules["starknet_py.net"] = net_mod
    sys.modules["starknet_py.net.full_node_client"] = fnc_mod
    sys.modules["starknet_py.hash.selector"] = selector_mod
    sys.modules["starknet_py.net.client_models"] = client_models_mod

from src.ops import network_checks
from src.ops.env import OpsConfig


class DummyClient:
    def __init__(self, gas_price: int = 42):
        self.gas_price = gas_price

    async def get_block(self, _latest):
        return self


class DummyOracle:
    def __init__(self, phantom_balance: Decimal, starknet_balance: Decimal, gas_price: int = 42):
        self._phantom = phantom_balance
        self._starknet = starknet_balance
        self.clients = {"starknet": DummyClient(gas_price)}
        self._initialized = False

    async def initialize(self):
        self._initialized = True

    async def get_balance(self, address: str, network: str):
        return self._phantom if network == "base" else self._starknet


def test_check_threshold_ready():
    cfg = OpsConfig(threshold_eth=Decimal("0.01"))
    oracle = DummyOracle(Decimal("0.001"), Decimal("0.02"))
    ready, balance = asyncio.run(network_checks.check_threshold(config=cfg, oracle=oracle))
    assert ready is True
    assert balance == Decimal("0.02")


def test_phantom_sweep_recommendation_insufficient():
    cfg = OpsConfig(threshold_eth=Decimal("0.02"), gas_reserve_eth=Decimal("0.002"))
    oracle = DummyOracle(Decimal("0.002"), Decimal("0.01"))
    result = asyncio.run(network_checks.phantom_sweep_recommendation(config=cfg, oracle=oracle))
    assert result["sweep_recommended"] is False
    assert result["sweep_amount"] == Decimal("0")


def test_get_gas_price_gwei():
    oracle = DummyOracle(Decimal("0"), Decimal("0"), gas_price=55)
    price = asyncio.run(network_checks.get_gas_price_gwei(oracle=oracle))
    assert price == 55
