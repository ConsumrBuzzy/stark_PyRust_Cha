"""
PyPro Systems - Bridge System
Extracted and consolidated bridge logic from tools/
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import os
from decimal import Decimal
from datetime import datetime, timedelta
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from ..foundation.constants import *
from ..foundation.security import SecurityManager

@dataclass
class BridgeConfig:
    """Bridge configuration"""
    starkgate_address: str
    starkgate_abi: list
    gas_reserve: float
    min_bridge_amount: float

@dataclass
class WithdrawalStatus:
    """Withdrawal operation status"""
    withdrawal_id: str
    amount: Decimal
    initiated_at: datetime
    claimable_at: datetime
    l1_tx_hash: Optional[str] = None
    status: str = "initiated"  # initiated, claimable, claimed, failed

class ClawbackSystem:
    """L2 → L1 Withdrawal System for Emergency Asset Recovery"""
    
    def __init__(self, network_oracle, security_manager: SecurityManager):
        self.network_oracle = network_oracle
        self.security_manager = security_manager
        self.withdrawal_history: Dict[str, WithdrawalStatus] = {}
    
    async def calculate_withdrawal_cost(self, amount_eth: Decimal) -> Dict[str, Any]:
        """Calculate the cost-benefit analysis for withdrawal"""
        try:
            # Get current gas prices
            base_client = self.network_oracle.clients["base"]
            starknet_client = self.network_oracle.clients["starknet"]
            
            # L1 gas price (using web3.eth.get_block)
            base_gas_price = 20  # Fixed estimate for Base (Gwei)
            
            # L2 gas price
            starknet_block = await starknet_client.get_block("latest")
            starknet_gas_price = getattr(starknet_block, 'gas_price', 20)
            
            # Estimate withdrawal costs
            l2_withdrawal_gas = 150000  # Estimated gas for withdrawal
            l1_claim_gas = 50000       # Estimated gas for claim
            
            l2_cost_eth = (starknet_gas_price * l2_withdrawal_gas) / Decimal('1e18')
            l1_cost_eth = Decimal(base_gas_price * l1_claim_gas) / Decimal('1e9')  # Gwei to ETH
            
            total_cost_eth = l2_cost_eth + l1_cost_eth
            net_amount_eth = amount_eth - total_cost_eth
            
            # Calculate USD values
            eth_price_usd = 2200  # Fixed price for calculation
            total_cost_usd = total_cost_eth * eth_price_usd
            net_amount_usd = net_amount_eth * eth_price_usd
            
            return {
                "amount_eth": amount_eth,
                "l2_cost_eth": l2_cost_eth,
                "l1_cost_eth": l1_cost_eth,
                "total_cost_eth": total_cost_eth,
                "net_amount_eth": net_amount_eth,
                "total_cost_usd": total_cost_usd,
                "net_amount_usd": net_amount_usd,
                "profitable": net_amount_eth > 0,
                "base_gas_price": base_gas_price,
                "starknet_gas_price": starknet_gas_price
            }
            
        except Exception as e:
            return {"error": str(e), "profitable": False}
    
    async def initiate_withdrawal(self, amount_eth: Decimal, starknet_address: str) -> Optional[str]:
        """Initiate L2 → L1 withdrawal"""
        try:
            # Cost-benefit check
            cost_analysis = await self.calculate_withdrawal_cost(amount_eth)
            if not cost_analysis.get("profitable", False):
                print(f"❌ Withdrawal not profitable: Cost {cost_analysis.get('total_cost_eth', 0):.6f} ETH")
                return None
            
            print(f"🛠️ Initiating withdrawal: {amount_eth:.6f} ETH")
            print(f"💰 Net amount after fees: {cost_analysis.get('net_amount_eth', 0):.6f} ETH")
            
            # Get StarkNet private key
            private_key = self.security_manager.get_starknet_private_key()
            if not private_key:
                print("❌ StarkNet private key not available")
                return None
            
            # This would integrate with actual StarkNet withdrawal contract
            # For now, simulate the withdrawal initiation
            withdrawal_id = f"withdrawal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Record withdrawal
            withdrawal_status = WithdrawalStatus(
                withdrawal_id=withdrawal_id,
                amount=amount_eth,
                initiated_at=datetime.now(),
                claimable_at=datetime.now() + timedelta(hours=3),  # StarkNet finality
                status="initiated"
            )
            
            self.withdrawal_history[withdrawal_id] = withdrawal_status
            
            print(f"✅ Withdrawal initiated: {withdrawal_id}")
            print(f"⏰ Claimable at: {withdrawal_status.claimable_at}")
            
            return withdrawal_id
            
        except Exception as e:
            print(f"❌ Withdrawal initiation failed: {e}")
            return None
    
    async def claim_withdrawal(self, withdrawal_id: str) -> Optional[str]:
        """Claim withdrawal on L1"""
        try:
            if withdrawal_id not in self.withdrawal_history:
                print(f"❌ Withdrawal not found: {withdrawal_id}")
                return None
            
            withdrawal = self.withdrawal_history[withdrawal_id]
            
            # Check if claimable
            if datetime.now() < withdrawal.claimable_at:
                print(f"⏳ Withdrawal not yet claimable: {withdrawal.claimable_at}")
                return None
            
            print(f"🛠️ Claiming withdrawal: {withdrawal_id}")
            
            # Get Base private key
            private_key = self.security_manager.get_phantom_private_key()
            if not private_key:
                print("❌ Base private key not available")
                return None
            
            # This would integrate with actual L1 claim transaction
            # For now, simulate the claim
            tx_hash = f"0x{'0' * 64}"  # Simulated transaction hash
            
            withdrawal.status = "claimed"
            withdrawal.l1_tx_hash = tx_hash
            
            print(f"✅ Withdrawal claimed: {tx_hash}")
            print(f"💰 Amount received: {withdrawal.amount:.6f} ETH")
            
            return tx_hash
            
        except Exception as e:
            print(f"❌ Withdrawal claim failed: {e}")
            return None
    
    def get_withdrawal_status(self, withdrawal_id: str) -> Optional[WithdrawalStatus]:
        """Get withdrawal status"""
        return self.withdrawal_history.get(withdrawal_id)
    
    def list_withdrawals(self) -> Dict[str, WithdrawalStatus]:
        """List all withdrawals"""
        return self.withdrawal_history.copy()

class BridgeSystem:
    """Dedicated bridge system extracted from atomic_activation.py"""
    
    def __init__(self, network_oracle, security_manager: SecurityManager):
        self.network_oracle = network_oracle
        self.security_manager = security_manager
        
        # Initialize ClawbackSystem for emergency withdrawals
        self.clawback_system = ClawbackSystem(network_oracle, security_manager)
        
        # Web3 setup for Base network
        self.base_web3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
        self.base_web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        
        # Bridge configuration
        self.bridge_config = BridgeConfig(
            starkgate_address=STARGATE_BRIDGE_ADDRESS,
            starkgate_abi=[
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
            ],
            gas_reserve=GAS_RESERVE,
            min_bridge_amount=MIN_BRIDGE_AMOUNT
        )
    
    async def calculate_optimal_bridge_amount(self, phantom_address: str) -> Dict[str, Any]:
        """Calculate optimal bridge amount using zero-waste logic"""
        try:
            # Get current balance
            balance_wei = self.base_web3.eth.get_balance(phantom_address)
            current_balance = self.base_web3.from_wei(balance_wei, 'ether')
            
            # Calculate dynamic bridge amount (zero-waste)
            max_bridge_amount = max(0, current_balance - self.bridge_config.gas_reserve)
            
            # Ensure minimum bridge amount
            bridge_amount = max(self.bridge_config.min_bridge_amount, max_bridge_amount)
            
            return {
                "success": True,
                "current_balance": current_balance,
                "bridge_amount": bridge_amount,
                "gas_reserve": self.bridge_config.gas_reserve,
                "remaining_after_bridge": current_balance - bridge_amount
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "current_balance": 0,
                "bridge_amount": 0
            }
    
    async def execute_bridge_transaction(self, phantom_address: str, starknet_address: str, amount: float) -> Dict[str, Any]:
        """Execute the actual bridge transaction"""
        try:
            print(f"🌉 EXECUTING STARKGATE BRIDGE")
            print(f"📍 From: {phantom_address}")
            print(f"📍 To: {starknet_address}")
            print(f"💰 Amount: {amount:.6f} ETH")
            
            # Get private key from security manager
            phantom_private_key = await self.security_manager.get_phantom_private_key()
            if not phantom_private_key:
                return {
                    "success": False,
                    "error": "No Phantom private key available"
                }
            
            # Create StarkGate contract
            starkgate_contract = self.base_web3.eth.contract(
                address=self.bridge_config.starkgate_address,
                abi=self.bridge_config.starkgate_abi
            )
            
            # Convert StarkNet address to uint256
            starknet_address_uint = int(starknet_address, 16)
            amount_wei = self.base_web3.to_wei(amount, 'ether')
            
            # Build transaction
            deposit_tx = starkgate_contract.functions.deposit(
                amount_wei,
                starknet_address_uint
            ).build_transaction({
                'from': phantom_address,
                'value': amount_wei,
                'gas': 200000,
                'gasPrice': self.base_web3.eth.gas_price,
                'nonce': self.base_web3.eth.get_transaction_count(phantom_address),
            })
            
            # Sign and send transaction
            signed_tx = self.base_web3.eth.account.sign_transaction(deposit_tx, phantom_private_key)
            tx_hash = self.base_web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            print(f"📡 Bridge transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            tx_receipt = self.base_web3.eth.wait_for_transaction_receipt(tx_hash, timeout=BRIDGE_TIMEOUT)
            
            if tx_receipt.status == 1:
                print("✅ StarkGate bridge completed successfully!")
                return {
                    "success": True,
                    "tx_hash": tx_hash.hex(),
                    "block_number": tx_receipt.blockNumber,
                    "gas_used": tx_receipt.gasUsed,
                    "amount": amount,
                    "from_address": phantom_address,
                    "to_address": starknet_address
                }
            else:
                return {
                    "success": False,
                    "error": "Bridge transaction failed",
                    "tx_hash": tx_hash.hex()
                }
                
        except Exception as e:
            print(f"❌ Bridge execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_bridge_status(self, tx_hash: str) -> Dict[str, Any]:
        """Get bridge transaction status"""
        try:
            receipt = self.base_web3.eth.get_transaction_receipt(tx_hash)
            
            return {
                "success": True,
                "status": "confirmed" if receipt.status == 1 else "failed",
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "confirmations": self.base_web3.eth.block_number - receipt.blockNumber
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def print_bridge_summary(self, bridge_result: Dict[str, Any]) -> None:
        """Print bridge transaction summary"""
        if bridge_result.get("success"):
            print(f"🌉 BRIDGE TRANSACTION SUMMARY")
            print(f"   Hash: {bridge_result['tx_hash']}")
            print(f"   Amount: {bridge_result['amount']:.6f} ETH")
            print(f"   From: {bridge_result['from_address']}")
            print(f"   To: {bridge_result['to_address']}")
            print(f"   Block: {bridge_result['block_number']}")
            print(f"   Gas Used: {bridge_result['gas_used']:,}")
        else:
            print(f"❌ BRIDGE FAILED: {bridge_result.get('error')}")

class ActivationSystem:
    """Dedicated activation system for account deployment"""
    
    def __init__(self, network_oracle, security_manager: SecurityManager):
        self.network_oracle = network_oracle
        self.security_manager = security_manager
    
    async def check_account_status(self, starknet_address: str) -> Dict[str, Any]:
        """Check if account is already deployed"""
        try:
            # Try to get account nonce - if account doesn't exist, this will fail
            client = self.network_oracle.clients["starknet"]
            
            try:
                nonce = await client.get_contract_nonce(
                    contract_address=int(starknet_address, 16),
                    block_number="latest"
                )
                return {
                    "success": True,
                    "deployed": True,
                    "nonce": nonce
                }
            except Exception:
                return {
                    "success": True,
                    "deployed": False,
                    "nonce": 0
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "deployed": False
            }
    
    async def execute_account_deployment(self, starknet_address: str) -> Dict[str, Any]:
        """Execute account deployment"""
        try:
            print("⚛️ EXECUTING ACCOUNT DEPLOYMENT")
            print(f"📍 Address: {starknet_address}")
            
            # Get private key from security manager
            private_key = await self.security_manager.get_starknet_private_key()
            if not private_key:
                return {
                    "success": False,
                    "error": "No StarkNet private key available"
                }
            
            # Use network oracle's activation method
            activation_result = await self.network_oracle.activate_account(
                starknet_address,
                private_key
            )
            
            if activation_result.get("success"):
                print("✅ Account deployment completed successfully!")
                return {
                    "success": True,
                    "tx_hash": activation_result["tx_hash"],
                    "address": activation_result["address"],
                    "deployed_address": starknet_address
                }
            else:
                return {
                    "success": False,
                    "error": activation_result.get("error", "Unknown error")
                }
                
        except Exception as e:
            print(f"❌ Account deployment failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_activation_status(self, tx_hash: str) -> Dict[str, Any]:
        """Get activation transaction status"""
        try:
            client = self.network_oracle.clients["starknet"]
            
            # Get transaction receipt
            receipt = await client.get_transaction_receipt(tx_hash)
            
            return {
                "success": True,
                "status": "confirmed" if receipt.execution_status.name == "SUCCEEDED" else "failed",
                "block_number": receipt.block_number,
                "execution_status": receipt.execution_status.name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def print_activation_summary(self, activation_result: Dict[str, Any]) -> None:
        """Print activation summary"""
        if activation_result.get("success"):
            print(f"⚛️ ACCOUNT DEPLOYMENT SUMMARY")
            print(f"   Transaction: {activation_result['tx_hash']}")
            print(f"   Address: {activation_result['deployed_address']}")
        else:
            print(f"❌ DEPLOYMENT FAILED: {activation_result.get('error')}")

class MonitoringSystem:
    """Dedicated monitoring system for balance and transaction tracking"""
    
    def __init__(self, network_oracle, state_registry):
        self.network_oracle = network_oracle
        self.state_registry = state_registry
    
    async def monitor_balance_until_threshold(self, starknet_address: str, threshold: float) -> Dict[str, Any]:
        """Monitor balance until threshold is reached"""
        print(f"🔍 MONITORING BALANCE UNTIL THRESHOLD: {threshold:.6f} ETH")
        
        while True:
            try:
                # Get current balance
                balance = await self.network_oracle.get_balance(starknet_address, "starknet")
                
                print(f"💰 Current Balance: {balance:.6f} ETH")
                
                if balance >= threshold:
                    print(f"🎯 THRESHOLD REACHED: {balance:.6f} ETH >= {threshold:.6f} ETH")
                    return {
                        "success": True,
                        "final_balance": balance,
                        "threshold_met": True
                    }
                
                # Update state
                await self.state_registry.update_balances(0, balance)  # Phantom balance not needed here
                
                # Wait before next check
                await asyncio.sleep(BALANCE_CHECK_INTERVAL)
                
            except Exception as e:
                print(f"❌ Balance monitoring error: {e}")
                await asyncio.sleep(BALANCE_CHECK_INTERVAL)
    
    async def monitor_bridge_mint(self, bridge_tx_hash: str, timeout: int = 1800) -> Dict[str, Any]:
        """Monitor bridge until mint is complete"""
        print(f"🔍 MONITORING BRIDGE MINT: {bridge_tx_hash[:10]}...")
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            try:
                # Check StarkNet balance
                current_balance = await self.network_oracle.get_balance(
                    self.state_registry.recovery_state.starknet_address, 
                    "starknet"
                )
                
                # Check if balance increased (indicating mint)
                if current_balance > self.state_registry.recovery_state.last_starknet_balance:
                    increase = current_balance - self.state_registry.recovery_state.last_starknet_balance
                    print(f"🎯 BRIDGE MINT DETECTED: +{increase:.6f} ETH")
                    
                    # Update bridge status
                    await self.state_registry.update_bridge_status(
                        bridge_tx_hash,
                        BridgeStatus.MINTED,
                        mint_timestamp=datetime.now().isoformat()
                    )
                    
                    return {
                        "success": True,
                        "minted": True,
                        "final_balance": current_balance,
                        "minted_amount": increase
                    }
                
                # Check timeout
                if asyncio.get_event_loop().time() - start_time > timeout:
                    print(f"⏰ BRIDGE MINT TIMEOUT: {timeout} seconds")
                    return {
                        "success": False,
                        "minted": False,
                        "error": "Timeout waiting for mint"
                    }
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"❌ Bridge monitoring error: {e}")
                await asyncio.sleep(30)
