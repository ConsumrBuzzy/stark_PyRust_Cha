"""Deployment engine for StarkNet accounts (deploy_account_v3 with resource bounds)."""
from __future__ import annotations

import os
from typing import Dict, Any, Optional

from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping
from starknet_py.hash.address import compute_address

from ..foundation.constants import ACCOUNT_CLASS_HASH
from ..foundation.network import NetworkOracle
from ..foundation.security import SecurityManager


class DeploymentEngine:
    """Handles StarkNet account deployments using configured resource bounds."""

    def __init__(self, network_oracle: NetworkOracle, security_manager: SecurityManager):
        self.network_oracle = network_oracle
        self.security_manager = security_manager

    async def _ensure_init(self) -> bool:
        if not self.network_oracle.is_initialized:
            if not await self.network_oracle.initialize():
                return False
        if not await self.security_manager.initialize():
            return False
        if not self.security_manager.is_vault_unlocked():
            await self.security_manager.unlock_vault_auto()
        return True

    def _default_resource_bounds(self) -> ResourceBoundsMapping:
        return ResourceBoundsMapping(
            l1_gas=ResourceBounds(max_amount=int(1e5), max_price_per_unit=int(1e13)),
            l1_data_gas=ResourceBounds(max_amount=int(1e4), max_price_per_unit=int(1e13)),
            l2_gas=ResourceBounds(max_amount=int(1e9), max_price_per_unit=int(1e17)),
        )

    async def deploy_account_v3(
        self,
        target_address: Optional[str] = None,
        class_hash: Optional[int] = None,
        salt: int = 0,
        resource_bounds: Optional[ResourceBoundsMapping] = None,
    ) -> Dict[str, Any]:
        if not await self._ensure_init():
            return {"success": False, "error": "Initialization failed"}

        rpc_client: FullNodeClient = self.network_oracle.clients.get("starknet")
        if not rpc_client:
            return {"success": False, "error": "StarkNet client unavailable"}

        priv_key_hex = await self.security_manager.get_starknet_private_key()
        if not priv_key_hex:
            return {"success": False, "error": "StarkNet private key unavailable"}

        key_pair = KeyPair.from_private_key(int(priv_key_hex, 16))
        target_addr_hex = target_address or os.getenv("STARKNET_WALLET_ADDRESS")
        if not target_addr_hex:
            return {"success": False, "error": "STARKNET_WALLET_ADDRESS not set"}

        target_addr_int = int(target_addr_hex, 16)
        class_hash_int = class_hash or int(ACCOUNT_CLASS_HASH, 16) if isinstance(ACCOUNT_CLASS_HASH, str) else ACCOUNT_CLASS_HASH

        computed_address = compute_address(
            class_hash=class_hash_int,
            constructor_calldata=[key_pair.public_key],
            salt=salt,
            deployer_address=0,
        )

        if computed_address != target_addr_int:
            return {
                "success": False,
                "error": "Address mismatch for provided key/class_hash",
                "computed_address": hex(computed_address),
                "target_address": target_addr_hex,
            }

        bounds = resource_bounds or self._default_resource_bounds()

        try:
            deploy_result = await Account.deploy_account_v3(
                address=target_addr_int,
                class_hash=class_hash_int,
                salt=salt,
                key_pair=key_pair,
                client=rpc_client,
                resource_bounds=bounds,
                constructor_calldata=[key_pair.public_key],
            )

            return {
                "success": True,
                "tx_hash": hex(deploy_result.hash),
                "deployed_address": hex(target_addr_int),
                "computed_address": hex(computed_address),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "computed_address": hex(computed_address)}
