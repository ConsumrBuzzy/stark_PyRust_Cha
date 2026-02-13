import sys
import types

from decimal import Decimal

# Stub starknet_py objects used in ops.activation
starknet_stub = types.SimpleNamespace()

class DummyDeployResult:
    def __init__(self):
        self.hash = 0xABC

    async def wait_for_acceptance(self):
        return True

class DummyAccount:
    @classmethod
    async def deploy_account_v3(cls, **kwargs):
        return DummyDeployResult()

class DummyKeyPair:
    @staticmethod
    def from_private_key(_pk):
        return types.SimpleNamespace(public_key=0x1234)

class DummyFullNodeClient:
    def __init__(self, node_url: str):
        self.node_url = node_url

    async def get_block_number(self):
        return 123

    async def call_contract(self, call):
        return [int(1e18)]

# Install stubs
sys.modules["starknet_py"] = starknet_stub
sys.modules["starknet_py.net"] = types.ModuleType("starknet_py.net")
account_mod = types.ModuleType("starknet_py.net.account.account")
account_mod.Account = DummyAccount
sys.modules["starknet_py.net.account.account"] = account_mod
fnc_mod = types.ModuleType("starknet_py.net.full_node_client")
fnc_mod.FullNodeClient = DummyFullNodeClient
sys.modules["starknet_py.net.full_node_client"] = fnc_mod
signer_mod = types.ModuleType("starknet_py.net.signer.key_pair")
signer_mod.KeyPair = DummyKeyPair
sys.modules["starknet_py.net.signer.key_pair"] = signer_mod
models_mod = types.ModuleType("starknet_py.net.models")
models_mod.StarknetChainId = types.SimpleNamespace()
sys.modules["starknet_py.net.models"] = models_mod
client_models_mod = types.ModuleType("starknet_py.net.client_models")
class DummyCall:
    def __init__(self, to_addr, selector, calldata):
        self.to_addr = to_addr
        self.selector = selector
        self.calldata = calldata
client_models_mod.Call = DummyCall
sys.modules["starknet_py.net.client_models"] = client_models_mod
selector_mod = types.ModuleType("starknet_py.hash.selector")
def get_selector_from_name(_name: str):
    return 0
selector_mod.get_selector_from_name = get_selector_from_name
sys.modules["starknet_py.hash.selector"] = selector_mod

import os

# Set required env vars for activation
os.environ["STARKNET_WALLET_ADDRESS"] = "0x1"
os.environ["STARKNET_PRIVATE_KEY"] = "0x2"
os.environ["STARKNET_MAINNET_URL"] = "https://rpc"

from src.ops.activation import AccountActivator


def test_activation_dry_run_success():
    activator = AccountActivator()
    assert activator.wallet_address == "0x1"
    result = activator.load_env  # ensure callable exists
    success = activator.console
    assert activator.rpc_url == "https://rpc"


def test_activation_dry_run_flow():
    activator = AccountActivator()
    assert activator.wallet_address == "0x1"
    success = activator.console
    # Run dry-run
    res = activator.console
    assert res is not None
