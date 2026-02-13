"""
PyPro Systems - Network Oracle
Unified network provider management
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from starknet_py.net.full_node_client import FullNodeClient

from ..foundation.constants import *

@dataclass
class NetworkConfig:
    """Network configuration"""
    name: str
    rpc_url: str
    chain_id: int
    native_token: str

class NetworkOracle:
    """Unified network provider and operations"""
    
    def __init__(self):
        self.networks = {
            "base": NetworkConfig("Base", BASE_RPC_URL, 8453, "ETH"),
            "starknet": NetworkConfig("StarkNet", STARKNET_RPC_URL, 0x534e5f4d41494e, "ETH")
        }
        
        self.clients: Dict[str, Any] = {}
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize all network clients"""
        try:
            # Initialize Base client
            self.clients["base"] = Web3(Web3.HTTPProvider(self.networks["base"].rpc_url))
            self.clients["base"].middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            
            # Initialize StarkNet client
            self.clients["starknet"] = FullNodeClient(node_url=self.networks["starknet"].rpc_url)
            
            # Test connections
            base_block = self.clients["base"].eth.block_number
            starknet_block = await self.clients["starknet"].get_block_number()
            
            print(f"✅ Base connected: Block {base_block}")
            print(f"✅ StarkNet connected: Block {starknet_block}")
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"❌ Network initialization failed: {e}")
            return False
    
    async def get_balance(self, address: str, network: str) -> float:
        """Get balance for address on specified network"""
        if not self.is_initialized or network not in self.clients:
            return 0.0
        
        try:
            if network == "base":
                balance_wei = self.clients["base"].eth.get_balance(address)
                return self.clients["base"].from_wei(balance_wei, 'ether')
            
            elif network == "starknet":
                from starknet_py.hash.selector import get_selector_from_name
                from starknet_py.net.client_models import Call
                
                call = Call(
                    to_addr=int(STARKNET_ETH_CONTRACT, 16),
                    selector=get_selector_from_name("balanceOf"),
                    calldata=[int(address, 16)]
                )
                
                result = await self.clients["starknet"].call_contract(call)
                return result[0] / 1e18
            
        except Exception as e:
            print(f"❌ Balance check failed on {network}: {e}")
            return 0.0
    
    async def execute_bridge(self, from_address: str, to_address: str, amount: float) -> Dict[str, Any]:
        """Execute StarkGate bridge from Base to StarkNet"""
        try:
            # Get private key
            import os
            phantom_private_key = os.getenv(PHANTOM_PRIVATE_KEY_ENV)
            if not phantom_private_key:
                phantom_private_key = os.getenv(SOLANA_PRIVATE_KEY_ENV)
            
            if not phantom_private_key:
                return {"success": False, "error": "No private key found"}
            
            # Create StarkGate contract
            starkgate_abi = [
                {
                    "inputs": [
                        {"name": "amount", "type": "uint256"},
                        {"name": "l2Recipient", "type": "uint256"}
                    ],
                    "name": "deposit",
                    "outputs": [],
                    "stateMutability": "payable",
                    "type": "function"
                }
            ]
            
            contract = self.clients["base"].eth.contract(
                address=STARGATE_BRIDGE_ADDRESS,
                abi=starkgate_abi
            )
            
            # Build transaction
            amount_wei = self.clients["base"].to_wei(amount, 'ether')
            starknet_address_uint = int(to_address, 16)
            
            tx = contract.functions.deposit(
                amount_wei,
                starknet_address_uint
            ).build_transaction({
                'from': from_address,
                'value': amount_wei,
                'gas': 200000,
                'gasPrice': self.clients["base"].eth.gas_price,
                'nonce': self.clients["base"].eth.get_transaction_count(from_address),
            })
            
            # Sign and send
            signed_tx = self.clients["base"].eth.account.sign_transaction(tx, phantom_private_key)
            tx_hash = self.clients["base"].eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for confirmation
            receipt = self.clients["base"].eth.wait_for_transaction_receipt(tx_hash, timeout=BRIDGE_TIMEOUT)
            
            if receipt.status == 1:
                return {
                    "success": True,
                    "tx_hash": tx_hash.hex(),
                    "block_number": receipt.blockNumber,
                    "gas_used": receipt.gasUsed,
                    "amount": amount
                }
            else:
                return {"success": False, "error": "Transaction failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def activate_account(self, starknet_address: str, private_key: str) -> Dict[str, Any]:
        """Activate StarkNet account"""
        try:
            from starknet_py.accounts.account import Account
            from starknet_py.net.signer.stark_curve_signer import KeyPair
            from starknet_py.hash.address import compute_address
            
            # Create key pair
            private_key_int = int(private_key, 16)
            key_pair = KeyPair.from_private_key(private_key_int)
            
            # Create account
            account = Account(
                address=starknet_address,
                key_pair=key_pair,
                client=self.clients["starknet"],
                chain=self.networks["starknet"].chain_id
            )
            
            # Deploy account (simplified)
            deploy_result = await account.deploy_account_v1(
                class_hash=ACCOUNT_CLASS_HASH,
                max_fee=int(MAX_FEE * 1e18)
            )
            
            return {
                "success": True,
                "tx_hash": hex(deploy_result.transaction_hash),
                "address": hex(deploy_result.contract_address)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def shutdown(self) -> None:
        """Shutdown network clients"""
        self.clients.clear()
        self.is_initialized = False
        print("✅ Network Oracle shutdown complete")
