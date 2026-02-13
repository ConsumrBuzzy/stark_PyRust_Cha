"""Rescue utilities: forced transfer and proxy-class deployment helpers."""
from __future__ import annotations

import os
from typing import Optional, Dict, Any, List

from rich.console import Console
from starknet_py.net.account.account import Account
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping
from starknet_py.net.models import StarknetChainId

from ..foundation.network import NetworkOracle
from ..foundation.security import SecurityManager
from .deployment import DeploymentEngine

console = Console()


def _default_resource_bounds() -> ResourceBoundsMapping:
    return ResourceBoundsMapping(
        l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
        l1_data_gas=ResourceBounds(max_amount=int(1e4), max_price_per_unit=int(1e13)),
        l2_gas=ResourceBounds(max_amount=int(1e9), max_price_per_unit=int(1e17)),
    )


class RescueEngine:
    def __init__(self, network_oracle: NetworkOracle, security_manager: SecurityManager):
        self.network_oracle = network_oracle
        self.security_manager = security_manager
        self.deployment_engine = DeploymentEngine(network_oracle, security_manager)

    async def _ensure_init(self) -> bool:
        if not self.network_oracle.is_initialized:
            if not await self.network_oracle.initialize():
                return False
        if not await self.security_manager.initialize():
            return False
        if not self.security_manager.is_vault_unlocked():
            await self.security_manager.unlock_vault_auto()
        return True

    async def force_transfer(self, from_address: str, destination: str, amount_wei: Optional[int] = None, leave_gas_wei: int = 500_000_000_000_000) -> Dict[str, Any]:
        if not await self._ensure_init():
            return {"success": False, "error": "Initialization failed"}

        rpc_client = self.network_oracle.clients.get("starknet")
        if not rpc_client:
            return {"success": False, "error": "StarkNet client unavailable"}

        priv_key_hex = await self.security_manager.get_starknet_private_key()
        if not priv_key_hex:
            return {"success": False, "error": "StarkNet private key unavailable"}

        key_pair = KeyPair.from_private_key(int(priv_key_hex, 16))
        account = Account(
            address=int(from_address, 16),
            client=rpc_client,
            key_pair=key_pair,
            chain=StarknetChainId.MAINNET,
        )

        try:
            balance = await account.get_balance()
        except Exception as e:
            return {"success": False, "error": f"Balance fetch failed: {e}"}

        if amount_wei is None:
            amount_wei = balance - leave_gas_wei
        if amount_wei <= 0:
            return {"success": False, "error": "Balance too low to cover gas"}

        try:
            transfer_call = account.prepare_transfer_call(
                to_addr=int(destination, 16),
                amount=amount_wei,
            )
            result = await account.execute_v3(
                calls=[transfer_call],
                resource_bounds=_default_resource_bounds(),
            )
            return {
                "success": True,
                "tx_hash": hex(result.hash),
                "amount_wei": amount_wei,
                "from": from_address,
                "to": destination,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def deploy_with_class_hash(self, class_hash: int, salt: int = 0, constructor_calldata: Optional[List[int]] = None) -> Dict[str, Any]:
        return await self.deployment_engine.deploy_account_v3(
            class_hash=class_hash,
            salt=salt,
            constructor_calldata=constructor_calldata,
        )
