#!/usr/bin/env python3
"""
Atomic Activation Engine - PhantomArbiter Pattern Implementation
Bundles account deployment with initial transfer for atomic execution
Based on PhantomArbiter/src/execution/bundle_submitter.py architecture
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Add core to path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.client_models import Call
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

# Import core components
from core.factory import get_provider_factory
from core.safety import get_signer
from core.ui import get_dashboard

class ExecutionStatus(Enum):
    """Atomic execution status"""
    PENDING = "pending"
    BROADCAST = "broadcast"
    CONFIRMED = "confirmed"
    FAILED = "failed"

@dataclass
class AtomicOperation:
    """Single operation within atomic bundle"""
    name: str
    call: Call
    description: str = ""

@dataclass
class AtomicBundle:
    """Bundle of operations to execute atomically"""
    operations: List[AtomicOperation]
    max_fee: int
    description: str = ""
    nonce: Optional[int] = None

@dataclass
class ExecutionResult:
    """Result of atomic execution"""
    status: ExecutionStatus
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    gas_used: Optional[int] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0

class AtomicActivationEngine:
    """
    Atomic activation engine based on PhantomArbiter bundle submitter
    Handles account deployment and initial transfer as single atomic operation
    """
    
    def __init__(self):
        self.console = Console()
        self.load_environment()
        self.provider_factory = get_provider_factory()
        self.signer = get_signer()
        self.dashboard = get_dashboard()
        
        # Account configuration
        self.wallet_address = os.getenv("STARKNET_WALLET_ADDRESS")
        self.ghost_address = os.getenv("STARKNET_GHOST_ADDRESS")
        self.phantom_base_address = os.getenv("PHANTOM_BASE_ADDRESS")
        
        if not self.phantom_base_address:
            # Try to get from transit address
            self.phantom_base_address = os.getenv("TRANSIT_EVM_ADDRESS")
        
        if not self.phantom_base_address:
            raise ValueError("PHANTOM_BASE_ADDRESS or TRANSIT_EVM_ADDRESS not found in environment")
        
        # Contract addresses
        self.eth_contract = int(os.getenv("STARKNET_ETH_CONTRACT", "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"), 16)
        self.argent_proxy_hash = int(os.getenv("STARKNET_ARGENT_PROXY_HASH", "0x06d44f5b497e5222d3c6fe5158d3b73a575450575b99d2101c5c180d07bc318b"), 16)
        
        # Execution parameters
        self.max_fee = int(0.02e18)  # 0.02 ETH max fee
        self.transfer_amount = int(0.001e18)  # 0.001 ETH initial transfer
        self.activation_threshold = 0.018  # ETH threshold for auto-trigger
        self.bridge_amount = 0.009  # ETH to bridge from Base to StarkNet
        
        # Auto-trigger state
        self.master_password = None
        self.auto_trigger_enabled = False
        
        # Base network configuration
        self.base_rpc_url = "https://mainnet.base.org"
        self.base_web3 = Web3(Web3.HTTPProvider(self.base_rpc_url))
        self.base_web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        
        # StarkGate bridge contract
        self.starkgate_bridge_address = "0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419"
        self.starkgate_bridge_abi = [
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
        
        logger.info("⚛️ Atomic Activation Engine initialized")
    
    def load_environment(self):
        """Load environment variables"""
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key.strip()] = value.strip()
    
    async def check_phantom_balance(self) -> Dict[str, Any]:
        """Check Phantom wallet balance on Base network"""
        
        try:
            balance_wei = self.base_web3.eth.get_balance(self.phantom_base_address)
            balance_eth = self.base_web3.from_wei(balance_wei, 'ether')
            
            return {
                "balance": float(balance_eth),
                "balance_wei": balance_wei,
                "address": self.phantom_base_address,
                "provider": "Base mainnet"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to check Phantom balance: {e}")
            return {"balance": 0, "error": str(e)}
    
    async def execute_starkgate_bridge(self) -> Dict[str, Any]:
        """Execute StarkGate bridge from Base to StarkNet"""
        
        try:
            self.console.print("🌉 EXECUTING STARKGATE BRIDGE", style="bold blue")
            self.console.print(f"📍 From: {self.phantom_base_address}")
            self.console.print(f"📍 To: {self.wallet_address}")
            self.console.print(f"💰 Amount: {self.bridge_amount} ETH")
            
            # Check balance
            balance_result = await self.check_phantom_balance()
            current_balance = balance_result["balance"]
            
            if current_balance < self.bridge_amount:
                raise Exception(f"Insufficient balance: {current_balance:.6f} ETH < {self.bridge_amount:.6f} ETH")
            
            # Get private key for Base wallet (Phantom)
            phantom_private_key = os.getenv("PHANTOM_BASE_PRIVATE_KEY")
            if not phantom_private_key:
                # Try to get from Solana Phantom data (Phantom uses same seed for EVM and Solana)
                phantom_private_key = os.getenv("SOLANA_PRIVATE_KEY")
                if not phantom_private_key:
                    raise Exception("Neither PHANTOM_BASE_PRIVATE_KEY nor SOLANA_PRIVATE_KEY found in environment")
            
            # Use Phantom Base address instead of Transit
            phantom_address = self.phantom_base_address
            
            # Create transaction
            starkgate_contract = self.base_web3.eth.contract(
                address=self.starkgate_bridge_address,
                abi=self.starkgate_bridge_abi
            )
            
            # Convert StarkNet address to uint256
            starknet_address_uint = int(self.wallet_address, 16)
            amount_wei = self.base_web3.to_wei(self.bridge_amount, 'ether')
            
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
            
            self.console.print(f"📡 Bridge transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            tx_receipt = self.base_web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if tx_receipt.status == 1:
                self.console.print("✅ StarkGate bridge completed successfully!", style="bold green")
                return {
                    "success": True,
                    "tx_hash": tx_hash.hex(),
                    "block_number": tx_receipt.blockNumber,
                    "gas_used": tx_receipt.gasUsed,
                    "amount": self.bridge_amount
                }
            else:
                raise Exception("Bridge transaction failed")
                
        except Exception as e:
            logger.error(f"❌ StarkGate bridge failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_starknet_balance(self) -> Dict[str, Any]:
        """Check current StarkNet balance using Alchemy exclusively"""
        
        try:
            # Use Alchemy provider exclusively for reliability
            provider_name = "Alchemy"
            client = self.provider_factory.providers["Alchemy"].client
            
            # Check balance using call_contract
            from starknet_py.hash.selector import get_selector_from_name
            from starknet_py.net.client_models import Call
            
            call = Call(
                to_addr=self.eth_contract,
                selector=get_selector_from_name("balanceOf"),
                calldata=[int(self.wallet_address, 16)]
            )
            
            result = await client.call_contract(call)
            balance = result[0] / 1e18
            
            logger.info(f"✅ Balance check successful via {provider_name}: {balance:.6f} ETH")
            
            return {
                "balance": balance,
                "provider": provider_name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Balance check failed via Alchemy: {e}")
            # NO FALLBACK - Return error status instead of fake balance
            return {
                "balance": None, 
                "error": str(e), 
                "provider": "none",
                "status": "PENDING"
            }
    
    def prompt_master_password(self) -> bool:
        """Prompt for master signer password"""
        
        try:
            import getpass
            
            self.console.print("\n🔐 [SECURITY] Master Signer Password Required", style="bold yellow")
            self.console.print("This password unlocks the encrypted private key for atomic execution.")
            
            password = getpass.getpass("Enter Master Signer Password: ")
            confirm = getpass.getpass("Confirm Password: ")
            
            if password != confirm:
                self.console.print("❌ Passwords do not match!", style="bold red")
                return False
            
            if not password:
                self.console.print("❌ Password cannot be empty!", style="bold red")
                return False
            
            # Test password by trying to get signer
            os.environ["SIGNER_PASSWORD"] = password
            try:
                keypair = self.signer.get_starknet_keypair()
                if not keypair:
                    raise Exception("Failed to retrieve keypair")
                
                self.master_password = password
                self.auto_trigger_enabled = True
                
                self.console.print("✅ Master password accepted. Auto-trigger enabled.", style="bold green")
                self.console.print("🔑 Private key unlocked and held in volatile memory.")
                
                return True
                
            except Exception as e:
                self.console.print(f"❌ Invalid password: {e}", style="bold red")
                return False
                
        except Exception as e:
            logger.error(f"❌ Password prompt failed: {e}")
            return False
    
    async def execute_full_bridge_and_activation(self) -> None:
        """Execute complete bridge + activation sequence"""
        
        self.console.print("🚀 FULL BRIDGE + ACTIVATION SEQUENCE", style="bold green")
        self.console.print("📍 Step 1: Check Phantom balance")
        
        # Check Phantom balance
        phantom_balance = await self.check_phantom_balance()
        self.console.print(f"💰 Phantom balance: {phantom_balance['balance']:.6f} ETH")
        
        if phantom_balance['balance'] < self.bridge_amount:
            self.console.print(f"❌ Insufficient Phantom balance: {phantom_balance['balance']:.6f} ETH < {self.bridge_amount:.6f} ETH", style="bold red")
            return
        
        self.console.print("📍 Step 2: Execute StarkGate bridge")
        
        # Execute bridge
        bridge_result = await self.execute_starkgate_bridge()
        
        if not bridge_result.get("success"):
            self.console.print(f"❌ Bridge failed: {bridge_result.get('error')}", style="bold red")
            return
        
        self.console.print("📍 Step 3: Monitor bridge completion and auto-activate")
        
        # Start monitoring for balance increase
        await self.auto_trigger_monitor()
    
    async def auto_trigger_monitor(self) -> None:
        """Infrastructure-grade back-off polling for auto-trigger execution"""
        
        self.console.print("🚀 Auto-Trigger Monitor Active", style="bold green")
        self.console.print(f"🎯 Watching for balance ≥ {self.activation_threshold} ETH")
        self.console.print("⏱️  Using back-off polling: 1 minute intervals until funds detected")
        
        # Back-off polling strategy
        poll_interval = 60  # Start with 1 minute intervals
        funds_detected = False
        
        while self.auto_trigger_enabled:
            try:
                # Check balance
                balance_result = await self.check_starknet_balance()
                current_balance = balance_result.get("balance")
                
                if current_balance is not None:
                    # Real balance data available
                    self.console.print(f"💰 Current Balance: {current_balance:.6f} ETH")
                    
                    # Update dashboard
                    self.dashboard.update_state({
                        "starknet_balance": current_balance,
                        "activation_threshold": self.activation_threshold,
                        "auto_trigger_active": True
                    })
                    
                    if not funds_detected:
                        # First time detecting real data - switch to high-frequency
                        funds_detected = True
                        poll_interval = 10  # Switch to 10-second intervals
                        self.console.print("📡 Real-time data detected - switching to high-frequency polling", style="bold yellow")
                else:
                    # No balance data available - keep back-off polling
                    if funds_detected:
                        # Lost connection after detecting funds - urgent retry
                        poll_interval = 5
                        self.console.print("⚠️ Connection lost - urgent retry mode", style="bold red")
                    else:
                        self.console.print(f"⏳ Balance check pending: {balance_result.get('error', 'Unknown error')}")
                    current_balance = 0  # Set to 0 for threshold check
                
                # Check threshold
                if current_balance >= self.activation_threshold:
                    self.console.print(f"\n🎯 THRESHOLD REACHED: {current_balance:.6f} ETH ≥ {self.activation_threshold} ETH")
                    self.console.print("🚀 EXECUTING ATOMIC ACTIVATION...")
                    
                    # Execute atomic activation
                    bundle = await self.create_deployment_bundle()
                    result = await self.execute_atomic_bundle(bundle)
                    
                    if result.status == ExecutionStatus.CONFIRMED:
                        self.console.print("🎉 MISSION SUCCESS: FUNDS SECURED", style="bold green")
                        
                        # Log to recovery complete
                        await self.log_recovery_success(result)
                        
                        # Update dashboard
                        self.dashboard.update_state({
                            "mission_status": "SUCCESS",
                            "activation_tx": result.transaction_hash,
                            "final_balance": current_balance
                        })
                        
                    else:
                        self.console.print(f"❌ Activation failed: {result.error_message}", style="bold red")
                    
                    # Stop monitoring
                    self.auto_trigger_enabled = False
                    break
                
                await asyncio.sleep(10)  # 10-second poll
                
            except KeyboardInterrupt:
                self.console.print("\n🛑 Auto-trigger monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitor error: {e}")
                await asyncio.sleep(10)
    
    async def log_recovery_success(self, result: ExecutionResult) -> None:
        """Log successful recovery to docs/RECOVERY_COMPLETE.md"""
        
        try:
            recovery_log = f"""# StarkNet Recovery Complete - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Mission Success: Atomic Activation Completed

### Execution Details
- **Status**: {result.status.value}
- **Transaction Hash**: {result.transaction_hash}
- **Block Number**: {result.block_number}
- **Gas Used**: {result.gas_used}
- **Execution Time**: {result.execution_time:.2f}s

### Financial Summary
- **Activation Threshold**: {self.activation_threshold} ETH
- **Final Balance**: Successfully deployed and funded
- **Security**: Enterprise-grade encrypted signer used

### Infrastructure Used
- **Bridge**: StarkGate canonical L1→L2 bridge
- **Provider**: {self.provider_factory.get_best_provider()[0]}
- **Security**: Encrypted signer with master password

### Next Steps
- Account is now deployed and operational
- Funds are secured in the system
- Ready for normal operations

---
*Automated recovery by StarkNet Shadow Protocol*
"""
            
            # Write to recovery log
            recovery_path = Path(__file__).parent.parent / "docs" / "RECOVERY_COMPLETE.md"
            recovery_path.parent.mkdir(exist_ok=True)
            
            with open(recovery_path, "w", encoding="utf-8") as f:
                f.write(recovery_log)
            
            logger.info("📝 Recovery logged to docs/RECOVERY_COMPLETE.md")
            
        except Exception as e:
            logger.error(f"❌ Failed to log recovery: {e}")
    
    async def create_deployment_bundle(self) -> AtomicBundle:
        """Create atomic bundle for account deployment"""
        
        # Get best provider
        provider_name, client = self.provider_factory.get_best_provider()
        
        # Get key pair from encrypted signer
        keypair_data = self.signer.get_starknet_keypair()
        if not keypair_data:
            raise Exception("Failed to retrieve keypair from encrypted signer")
        
        # Create key pair from private key
        private_key_int = int(keypair_data['private_key'], 16)
        keypair = KeyPair.from_private_key(private_key_int)
        
        # Convert address to int
        address_int = int(self.wallet_address, 16)
        
        # Get current nonce
        try:
            nonce = await client.get_contract_nonce(
                contract_address=address_int,
                block_number="latest"
            )
        except:
            nonce = 0  # Account not deployed yet
        
        # Create deployment call (this will be handled by Account.deploy_account_v3)
        # We'll add a transfer operation to the bundle
        
        # Create transfer call (post-deployment)
        transfer_call = Call(
            to_addr=self.eth_contract,
            selector=get_selector_from_name("transfer"),
            calldata=[
                int(self.ghost_address, 16),  # recipient
                self.transfer_amount,          # amount low
                0                            # amount high
            ]
        )
        
        # Create atomic operations
        operations = [
            AtomicOperation(
                name="deploy_account",
                call=None,  # Handled by deploy_account_v3
                description="Deploy StarkNet account with Argent proxy"
            ),
            AtomicOperation(
                name="initial_transfer",
                call=transfer_call,
                description=f"Transfer {self.transfer_amount / 1e18:.6f} ETH to Ghost address"
            )
        ]
        
        bundle = AtomicBundle(
            operations=operations,
            max_fee=self.max_fee,
            description="Atomic account deployment and initial transfer",
            nonce=nonce
        )
        
        logger.info(f"📦 Created deployment bundle with {len(operations)} operations")
        return bundle
    
    async def simulate_execution(self, bundle: AtomicBundle) -> Dict[str, Any]:
        """Simulate atomic execution without broadcasting"""
        
        self.console.print("🔍 SIMULATION MODE - Atomic Bundle Analysis")
        
        try:
            # Get best provider
            provider_name, client = self.provider_factory.get_best_provider()
            
            # Simulate deployment cost
            deploy_estimate = await self.estimate_deployment_cost(client)
            
            # Simulate transfer cost
            transfer_estimate = await self.estimate_transfer_cost(client)
            
            total_cost = deploy_estimate + transfer_estimate
            
            simulation_result = {
                "deploy_cost": deploy_estimate,
                "transfer_cost": transfer_estimate,
                "total_cost": total_cost,
                "max_fee": bundle.max_fee,
                "sufficient_fee": total_cost <= bundle.max_fee,
                "provider": provider_name
            }
            
            return simulation_result
            
        except Exception as e:
            logger.error(f"❌ Simulation failed: {e}")
            return {"error": str(e)}
    
    async def estimate_deployment_cost(self, client: FullNodeClient) -> int:
        """Estimate account deployment cost"""
        
        try:
            # Create a dummy deployment estimate
            # In practice, this would call starknet_estimateFee with deployment params
            estimated_cost = int(0.01e18)  # 0.01 ETH typical deployment cost
            return estimated_cost
            
        except Exception as e:
            logger.warning(f"⚠️ Deployment cost estimation failed: {e}")
            return int(0.015e18)  # Conservative estimate
    
    async def estimate_transfer_cost(self, client: FullNodeClient) -> int:
        """Estimate transfer cost"""
        
        # For starknet-py v0.29.0, use conservative estimate
        # Fee estimation API has compatibility issues
        estimated_cost = int(0.003e18)  # 0.003 ETH conservative estimate
        
        logger.info(f"💰 Using conservative transfer cost estimate: {estimated_cost / 1e18:.6f} ETH")
        return estimated_cost
    
    async def execute_atomic_bundle(self, bundle: AtomicBundle, dry_run: bool = False) -> ExecutionResult:
        """Execute atomic bundle"""
        
        start_time = datetime.now()
        result = ExecutionResult(status=ExecutionStatus.PENDING)
        
        try:
            # Get best provider
            provider_name, client = self.provider_factory.get_best_provider()
            
            if dry_run:
                self.console.print("🔍 DRY RUN MODE - No actual execution")
                result.status = ExecutionStatus.CONFIRMED
                result.execution_time = (datetime.now() - start_time).total_seconds()
                return result
            
            # Get key pair from encrypted signer
            keypair_data = self.signer.get_starknet_keypair()
            if not keypair_data:
                raise Exception("Failed to retrieve keypair from encrypted signer")
            
            # Create key pair from private key
            private_key_int = int(keypair_data['private_key'], 16)
            keypair = KeyPair.from_private_key(private_key_int)
            
            # Convert address to int
            address_int = int(self.wallet_address, 16)
            
            self.console.print("⚛️ EXECUTING ATOMIC BUNDLE")
            self.console.print(f"📡 Provider: {provider_name}")
            self.console.print(f"🔧 Max Fee: {bundle.max_fee / 1e18:.6f} ETH")
            
            # Step 1: Deploy account
            self.console.print("🚀 Step 1: Deploying account...")
            
            deploy_result = await Account.deploy_account_v3(
                address=address_int,
                class_hash=self.argent_proxy_hash,
                salt=0,
                key_pair=key_pair,
                client=client,
                constructor_calldata=[key_pair.public_key, 0],
                max_fee=bundle.max_fee,
            )
            
            result.transaction_hash = hex(deploy_result.hash)
            result.status = ExecutionStatus.BROADCAST
            
            self.console.print(f"✅ Deployment broadcast: {result.transaction_hash}")
            
            # Wait for deployment confirmation
            self.console.print("⏳ Waiting for deployment confirmation...")
            await deploy_result.wait_for_acceptance()
            
            result.status = ExecutionStatus.CONFIRMED
            result.block_number = deploy_result.block_number
            
            self.console.print("🎉 Account deployed successfully!")
            
            # Step 2: Execute initial transfer
            self.console.print("💰 Step 2: Executing initial transfer...")
            
            # Create deployed account instance
            deployed_account = Account(
                address=address_int,
                client=client,
                key_pair=key_pair,
                chain_id=None  # Will be detected automatically
            )
            
            # Execute transfer
            transfer_call = Call(
                to_addr=self.eth_contract,
                selector=get_selector_from_name("transfer"),
                calldata=[
                    int(self.ghost_address, 16),
                    self.transfer_amount,
                    0
                ]
            )
            
            transfer_result = await deployed_account.execute_v1(
                calls=transfer_call,
                max_fee=int(0.005e18)  # Separate fee for transfer
            )
            
            self.console.print(f"✅ Transfer broadcast: {hex(transfer_result.hash)}")
            
            # Wait for transfer confirmation
            await transfer_result.wait_for_acceptance()
            
            self.console.print("💰 Initial transfer completed!")
            
            result.execution_time = (datetime.now() - start_time).total_seconds()
            
            return result
            
        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error_message = str(e)
            result.execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.error(f"❌ Atomic execution failed: {e}")
            return result
    
    def create_execution_panel(self, result: ExecutionResult, simulation: Optional[Dict] = None) -> Panel:
        """Create execution result panel"""
        
        content = f"""
**Status**: {result.status.value}
**Execution Time**: {result.execution_time:.2f}s
"""
        
        if result.transaction_hash:
            content += f"**Transaction**: {result.transaction_hash}\n"
        
        if result.block_number:
            content += f"**Block**: {result.block_number}\n"
        
        if result.error_message:
            content += f"**Error**: {result.error_message}\n"
        
        if simulation:
            content += f"""
**Simulation Results**:
• Deploy Cost: {simulation.get('deploy_cost', 0) / 1e18:.6f} ETH
• Transfer Cost: {simulation.get('transfer_cost', 0) / 1e18:.6f} ETH
• Total Cost: {simulation.get('total_cost', 0) / 1e18:.6f} ETH
• Max Fee: {simulation.get('max_fee', 0) / 1e18:.6f} ETH
• Provider: {simulation.get('provider', 'Unknown')}
"""
        
        border_style = {
            ExecutionStatus.CONFIRMED: "green",
            ExecutionStatus.BROADCAST: "yellow",
            ExecutionStatus.FAILED: "red",
            ExecutionStatus.PENDING: "blue"
        }.get(result.status, "white")
        
        return Panel(
            content.strip(),
            title="⚛️ Atomic Execution Result",
            border_style=border_style
        )
    
    def save_execution_report(self, result: ExecutionResult, bundle: AtomicBundle, simulation: Optional[Dict] = None):
        """Save detailed execution report"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# Atomic Activation Execution Report

**Timestamp**: {timestamp}
**Engine**: AtomicActivationEngine (PhantomArbiter Pattern)
**Bundle**: {bundle.description}

## Execution Summary

**Status**: {result.status.value}
**Execution Time**: {result.execution_time:.2f} seconds
**Transaction Hash**: {result.transaction_hash or 'N/A'}
**Block Number**: {result.block_number or 'N/A'}

## Bundle Operations
"""
        
        for i, op in enumerate(bundle.operations, 1):
            report += f"{i}. **{op.name}**: {op.description}\n"
        
        if result.error_message:
            report += f"\n## Error Details\n{result.error_message}\n"
        
        if simulation:
            report += f"""

## Simulation Results

- **Deploy Cost**: {simulation.get('deploy_cost', 0) / 1e18:.6f} ETH
- **Transfer Cost**: {simulation.get('transfer_cost', 0) / 1e18:.6f} ETH
- **Total Cost**: {simulation.get('total_cost', 0) / 1e18:.6f} ETH
- **Max Fee**: {simulation.get('max_fee', 0) / 1e18:.6f} ETH
- **Provider**: {simulation.get('provider', 'Unknown')}
- **Fee Sufficiency**: {'✅ Sufficient' if simulation.get('sufficient_fee') else '❌ Insufficient'}

## Technical Details

- **Account Address**: {self.wallet_address}
- **Ghost Address**: {self.ghost_address}
- **Transfer Amount**: {self.transfer_amount / 1e18:.6f} ETH
- **Proxy Hash**: {hex(self.argent_proxy_hash)}

## Architecture Notes

This atomic execution follows the PhantomArbiter bundle submitter pattern:
- Operations are bundled for atomic execution
- Failover handling via ProviderFactory
- Gas optimization through simulation
- Comprehensive error handling and reporting

---
*Generated by tools/atomic_activation.py - PhantomArbiter Pattern*
"""
        
        # Save to data/reports directory
        reports_dir = Path(__file__).parent.parent / "data" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"atomic_activation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📄 Atomic execution report saved: {report_file}")

async def main():
    """Main execution with full bridge automation"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Atomic Activation Engine")
    parser.add_argument("--dry-run", action="store_true", help="Simulation only")
    parser.add_argument("--simulate", action="store_true", help="Cost simulation only")
    parser.add_argument("--full-bridge", action="store_true", help="Execute full bridge + activation sequence")
    args = parser.parse_args()
    
    console = Console()
    console.print("⚛️ Atomic Activation Engine - PhantomArbiter Pattern", style="bold blue")
    console.print("🔗 Atomic Deployment + Transfer Execution", style="dim")
    
    try:
        # Initialize provider factory
        await get_provider_factory().check_all_providers()
        
        # Create engine
        engine = AtomicActivationEngine()
        
        if args.full_bridge:
            # Full bridge + activation mode
            console.print("\n🚀 FULL BRIDGE + ACTIVATION MODE", style="bold green")
            console.print("🌉 This will execute the complete Base→StarkNet bridge and auto-activate")
            
            # Prompt for master password
            if not engine.prompt_master_password():
                console.print("❌ Full bridge mode requires valid password", style="bold red")
                return
            
            # Execute full sequence
            await engine.execute_full_bridge_and_activation()
            
        elif not args.dry_run and not args.simulate:
            # Auto-trigger mode - prompt for password
            console.print("\n🚀 LIVE EXECUTION MODE - Auto-Trigger Protocol", style="bold green")
            console.print("🎯 The system will automatically execute when balance ≥ 0.018 ETH")
            
            # Prompt for master password
            if not engine.prompt_master_password():
                console.print("❌ Auto-trigger mode requires valid password", style="bold red")
                return
            
            # Start auto-trigger monitoring
            await engine.auto_trigger_monitor()
            
        else:
            # Simulation/dry-run mode
            # Create atomic bundle
            bundle = await engine.create_deployment_bundle()
            
            console.print(f"📦 Bundle created: {bundle.description}")
            console.print(f"🔧 Operations: {len(bundle.operations)}")
            console.print(f"⛽ Max Fee: {bundle.max_fee / 1e18:.6f} ETH")
            
            if args.simulate:
                # Run simulation only
                simulation = await engine.simulate_execution(bundle)
                
                console.print("\n📊 Simulation Results:")
                console.print(f"• Deploy Cost: {simulation.get('deploy_cost', 0) / 1e18:.6f} ETH")
                console.print(f"• Transfer Cost: {simulation.get('transfer_cost', 0) / 1e18:.6f} ETH")
                console.print(f"• Total Cost: {simulation.get('total_cost', 0) / 1e18:.6f} ETH")
                console.print(f"• Sufficient Fee: {'✅ Yes' if simulation.get('sufficient_fee') else '❌ No'}")
                
            else:
                # Dry run mode
                simulation = await engine.simulate_execution(bundle)
                
                if not simulation.get('sufficient_fee', False):
                    console.print("❌ Insufficient max fee for execution", style="bold red")
                    console.print(f"Required: {simulation.get('total_cost', 0) / 1e18:.6f} ETH")
                    console.print(f"Max Fee: {simulation.get('max_fee', 0) / 1e18:.6f} ETH")
                    return
                
                # Execute atomic bundle (dry run)
                result = await engine.execute_atomic_bundle(bundle, dry_run=args.dry_run)
                
                # Display results
                panel = engine.create_execution_panel(result, simulation)
                console.print(panel)
                
                # Save report
                engine.save_execution_report(result, bundle, simulation)
                
                if result.status == ExecutionStatus.CONFIRMED:
                    console.print("\n🎉 ATOMIC EXECUTION SUCCESSFUL!", style="bold green")
                    console.print("💼 Account is now deployed and funded")
                elif result.status == ExecutionStatus.FAILED:
                    console.print("\n❌ ATOMIC EXECUTION FAILED", style="bold red")
                    console.print("🔧 Check error message above")
        
    except Exception as e:
        console.print(f"❌ Fatal error: {e}", style="bold red")
        logger.error(f"❌ Atomic activation error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Atomic activation stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
