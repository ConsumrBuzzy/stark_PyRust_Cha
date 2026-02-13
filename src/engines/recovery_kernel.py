"""
PyPro Systems - Recovery Kernel
Unified State Machine for StarkNet Account Recovery
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
import asyncio
import json
from pathlib import Path
from datetime import datetime

from ..foundation.constants import *
from ..foundation.security import SecurityManager
from ..foundation.network import NetworkOracle
from ..foundation.state import StateRegistry, RecoveryState, BridgeStatus, AccountStatus
from .bridge_system import BridgeSystem, ActivationSystem, MonitoringSystem
from .enhanced_monitoring import EnhancedMonitoringSystem, AtomicBundle, MonitoringMode

class RecoveryPhase(Enum):
    """Recovery phase states"""
    INITIALIZING = "initializing"
    SECURITY_UNLOCKED = "security_unlocked"
    BRIDGE_EXECUTING = "bridge_executing"
    BRIDGE_CONFIRMED = "bridge_confirmed"
    MINT_WAITING = "mint_waiting"
    MINT_CONFIRMED = "mint_confirmed"
    ACTIVATION_EXECUTING = "activation_executing"
    ACTIVATION_COMPLETE = "activation_complete"
    MISSION_SUCCESS = "mission_success"
    MISSION_FAILED = "mission_failed"

class RecoveryKernel:
    """Unified Recovery Kernel - Single Source of Truth"""
    
    def __init__(self, phantom_address: str, starknet_address: str):
        self.phantom_address = phantom_address
        self.starknet_address = starknet_address
        
        # Core components
        self.security_manager: Optional[SecurityManager] = None
        self.network_oracle: Optional[NetworkOracle] = None
        self.state_registry: Optional[StateRegistry] = None
        
        # Dedicated systems
        self.bridge_system: Optional[BridgeSystem] = None
        self.activation_system: Optional[ActivationSystem] = None
        self.monitoring_system: Optional[MonitoringSystem] = None
        self.enhanced_monitoring: Optional[EnhancedMonitoringSystem] = None
        
        # Atomic bundle system
        self.atomic_bundle: Optional[AtomicBundle] = None
        
        # State management
        self.current_phase: RecoveryPhase = RecoveryPhase.INITIALIZING
        self.recovery_state: Optional[RecoveryState] = None
        
        # Mission control
        self.is_running = False
        self.max_bridge_attempts = 3
        
        # Phase handlers
        self.phase_handlers = {
            RecoveryPhase.INITIALIZING: self._handle_initializing,
            RecoveryPhase.SECURITY_UNLOCKED: self._handle_security_unlocked,
            RecoveryPhase.BRIDGE_EXECUTING: self._handle_bridge_executing,
            RecoveryPhase.BRIDGE_CONFIRMED: self._handle_bridge_confirmed,
            RecoveryPhase.MINT_WAITING: self._handle_mint_waiting,
            RecoveryPhase.MINT_CONFIRMED: self._handle_mint_confirmed,
            RecoveryPhase.ACTIVATION_EXECUTING: self._handle_activation_executing,
            RecoveryPhase.ACTIVATION_COMPLETE: self._handle_activation_complete,
            RecoveryPhase.MISSION_SUCCESS: self._handle_mission_success,
            RecoveryPhase.MISSION_FAILED: self._handle_mission_failed,
        }
    
    async def initialize(self) -> bool:
        """Initialize the Recovery Kernel"""
        print("🚀 Initializing Recovery Kernel...")
        
        try:
            # Initialize state registry
            self.state_registry = StateRegistry()
            
            # Try to load existing state
            existing_state = await self.state_registry.load_state()
            if existing_state:
                self.recovery_state = existing_state
                self.current_phase = RecoveryPhase(existing_state.current_phase)
                print(f"📂 Loaded previous recovery state: {self.current_phase.value}")
            else:
                # Initialize new state
                self.recovery_state = await self.state_registry.initialize_state(
                    self.phantom_address, 
                    self.starknet_address
                )
                self.current_phase = RecoveryPhase.INITIALIZING
                print("📂 Created new recovery state")
            
            # Initialize Network Oracle
            self.network_oracle = NetworkOracle()
            if not await self.network_oracle.initialize():
                print("❌ Failed to initialize Network Oracle")
                return False
            
            # Initialize Security Manager
            self.security_manager = SecurityManager()
            if not await self.security_manager.initialize():
                print("❌ Failed to initialize Security Manager")
                return False
            
            # Initialize dedicated systems
            self.bridge_system = BridgeSystem(self.network_oracle, self.security_manager)
            self.activation_system = ActivationSystem(self.network_oracle, self.security_manager)
            self.monitoring_system = MonitoringSystem(self.network_oracle, self.state_registry)
            self.enhanced_monitoring = EnhancedMonitoringSystem(self.network_oracle, self.state_registry)
            
            # Initialize atomic bundle
            self.atomic_bundle = AtomicBundle(self.activation_system)
            
            # Initialize UI if available
            self.enhanced_monitoring.initialize_ui()
            
            # Check if security is already unlocked
            if self.recovery_state.security_unlocked:
                self.current_phase = RecoveryPhase.BRIDGE_EXECUTING
                print("🔓 Security already unlocked from previous session")
            
            self.is_running = True
            print("✅ Recovery Kernel initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Kernel initialization failed: {e}")
            return False
    
    async def execute_recovery(self) -> bool:
        """Execute the complete recovery mission"""
        if not self.is_running:
            return False
        
        print("🎯 Starting Recovery Mission...")
        
        try:
            while self.is_running and self.current_phase not in [
                RecoveryPhase.MISSION_SUCCESS, 
                RecoveryPhase.MISSION_FAILED
            ]:
                # Get current phase handler
                handler = self.phase_handlers.get(self.current_phase)
                if not handler:
                    print(f"❌ No handler for phase: {self.current_phase}")
                    await self._transition_to(RecoveryPhase.MISSION_FAILED)
                    continue
                
                # Execute phase handler
                print(f"🔄 Executing phase: {self.current_phase.value}")
                await handler()
                
                # Brief pause between phases
                await asyncio.sleep(2)
            
            return self.current_phase == RecoveryPhase.MISSION_SUCCESS
            
        except Exception as e:
            print(f"❌ Recovery execution failed: {e}")
            await self._transition_to(RecoveryPhase.MISSION_FAILED)
            return False
    
    async def _transition_to(self, new_phase: RecoveryPhase, message: str = "") -> None:
        """Transition to a new phase"""
        old_phase = self.current_phase
        self.current_phase = new_phase
        
        # Update state
        if self.recovery_state:
            self.recovery_state.current_phase = new_phase.value
            await self.state_registry.update_state(current_phase=new_phase.value)
        
        print(f"🔄 Phase transition: {old_phase.value} → {new_phase.value}")
        if message:
            print(f"   📝 {message}")
    
    # Phase Handlers
    async def _handle_initializing(self) -> None:
        """Handle initializing phase"""
        await self._transition_to(RecoveryPhase.SECURITY_UNLOCKED, "Ready for security unlock")
    
    async def _handle_security_unlocked(self) -> None:
        """Handle security unlocked phase"""
        if not self.security_manager or not self.security_manager.is_vault_unlocked():
            print("🔐 Security vault locked - manual unlock required")
            return
        
        await self._transition_to(RecoveryPhase.BRIDGE_EXECUTING, "Security unlocked, ready for bridge")
    
    async def _handle_bridge_executing(self) -> None:
        """Handle bridge executing phase"""
        # Check if we already have confirmed bridges
        confirmed_bridges = [tx for tx in self.recovery_state.bridge_transactions 
                           if tx.status == BridgeStatus.CONFIRMED]
        
        if confirmed_bridges:
            print(f"✅ Found {len(confirmed_bridges)} confirmed bridges")
            await self._transition_to(RecoveryPhase.BRIDGE_CONFIRMED, "Bridges already confirmed")
            return
        
        # Calculate optimal bridge amount
        bridge_calc = await self.bridge_system.calculate_optimal_bridge_amount(self.phantom_address)
        
        if not bridge_calc["success"]:
            print(f"❌ Bridge calculation failed: {bridge_calc['error']}")
            await self._transition_to(RecoveryPhase.MISSION_FAILED, "Bridge calculation failed")
            return
        
        print(f"💰 Available Balance: {bridge_calc['current_balance']:.6f} ETH")
        print(f"🌉 Bridge Amount: {bridge_calc['bridge_amount']:.6f} ETH")
        print(f"⛽ Gas Reserve: {bridge_calc['gas_reserve']:.6f} ETH")
        
        if bridge_calc['bridge_amount'] <= 0:
            print(f"❌ Insufficient balance: {bridge_calc['current_balance']:.6f} ETH <= {bridge_calc['gas_reserve']:.6f} ETH")
            await self._transition_to(RecoveryPhase.MISSION_FAILED, "Insufficient Phantom balance")
            return
        
        # Execute bridge transaction
        bridge_result = await self.bridge_system.execute_bridge_transaction(
            self.phantom_address,
            self.starknet_address,
            bridge_calc['bridge_amount']
        )
        
        if bridge_result.get("success"):
            # Add to state
            await self.state_registry.add_bridge_transaction(
                bridge_result["tx_hash"],
                bridge_result["amount"],
                self.phantom_address,
                self.starknet_address
            )
            
            # Update balances
            await self.state_registry.update_balances(
                bridge_calc['current_balance'] - bridge_result['amount'],
                self.recovery_state.last_starknet_balance
            )
            
            self.bridge_system.print_bridge_summary(bridge_result)
            await self._transition_to(RecoveryPhase.BRIDGE_CONFIRMED, f"Bridge executed: {bridge_result['amount']:.6f} ETH")
        else:
            print(f"❌ Bridge failed: {bridge_result.get('error')}")
            await self._transition_to(RecoveryPhase.MISSION_FAILED, "Bridge execution failed")
    
    async def _handle_bridge_confirmed(self) -> None:
        """Handle bridge confirmed phase"""
        # Update bridge statuses
        for tx in self.recovery_state.bridge_transactions:
            if tx.status == BridgeStatus.PENDING:
                # Check transaction status on Base
                try:
                    # This would check the Base transaction status
                    # For now, assume confirmed
                    await self.state_registry.update_bridge_status(
                        tx.tx_hash, 
                        BridgeStatus.CONFIRMED,
                        block_number=42091705  # Example
                    )
                except Exception as e:
                    print(f"⚠️ Bridge status check failed: {e}")
        
        await self._transition_to(RecoveryPhase.MINT_WAITING, "Bridge confirmed, waiting for mint")
    
    async def _handle_mint_waiting(self) -> None:
        """Handle mint waiting phase"""
        # Check StarkNet balance
        starknet_balance = await self.network_oracle.get_balance(self.starknet_address, "starknet")
        await self.state_registry.update_balances(self.recovery_state.last_phantom_balance, starknet_balance)
        
        print(f"💰 StarkNet balance: {starknet_balance:.6f} ETH")
        
        if starknet_balance >= ACTIVATION_THRESHOLD:
            print(f"🎯 Mint confirmed: {starknet_balance:.6f} ETH")
            
            # Update bridge statuses to minted
            for tx in self.recovery_state.bridge_transactions:
                if tx.status == BridgeStatus.CONFIRMED:
                    await self.state_registry.update_bridge_status(
                        tx.tx_hash, 
                        BridgeStatus.MINTED,
                        mint_timestamp=datetime.now().isoformat()
                    )
            
            await self._transition_to(RecoveryPhase.MINT_CONFIRMED, "Mint complete")
        else:
            needed = ACTIVATION_THRESHOLD - starknet_balance
            print(f"⏳ Need {needed:.6f} more ETH")
            # Stay in this phase and keep checking
    
    async def _handle_mint_confirmed(self) -> None:
        """Handle mint confirmed phase"""
        await self._transition_to(RecoveryPhase.ACTIVATION_EXECUTING, "Mint confirmed, ready for activation")
    
    async def _handle_activation_executing(self) -> None:
        """Handle activation executing phase"""
        print("⚛️ Executing account activation...")
        
        # Check account status first
        account_status = await self.activation_system.check_account_status(self.starknet_address)
        
        if account_status.get("success") and account_status.get("deployed"):
            print("✅ Account already deployed")
            await self._transition_to(RecoveryPhase.ACTIVATION_COMPLETE, "Account already exists")
            return
        
        # Execute account deployment
        activation_result = await self.activation_system.execute_account_deployment(self.starknet_address)
        
        if activation_result.get("success"):
            await self.state_registry.update_account_status(
                AccountStatus.DEPLOYED, 
                activation_result.get("tx_hash")
            )
            
            self.activation_system.print_activation_summary(activation_result)
            await self._transition_to(RecoveryPhase.ACTIVATION_COMPLETE, "Account activation successful")
        else:
            print(f"❌ Activation failed: {activation_result.get('error')}")
            await self.state_registry.update_account_status(AccountStatus.FAILED)
            await self._transition_to(RecoveryPhase.MISSION_FAILED, "Account activation failed")
    
    async def _handle_activation_complete(self) -> None:
        """Handle activation complete phase"""
        await self._transition_to(RecoveryPhase.MISSION_SUCCESS, "Mission completed successfully")
    
    async def _handle_mission_success(self) -> None:
        """Handle mission success phase"""
        print("🎉 MISSION SUCCESS!")
        await self.state_registry.complete_mission()
        self.is_running = False
    
    async def _handle_mission_failed(self) -> None:
        """Handle mission failed phase"""
        print("❌ MISSION FAILED!")
        await self.state_registry.complete_mission()
        self.is_running = False
    
    async def unlock_security(self, password: str) -> bool:
        """Unlock security vault"""
        if not self.security_manager:
            return False
        
        success = await self.security_manager.unlock_vault(password)
        if success:
            await self.state_registry.set_security_unlocked(True)
            await self._transition_to(RecoveryPhase.BRIDGE_EXECUTING, "Security vault unlocked")
        
        return success
    
    def print_status(self) -> None:
        """Print current status"""
        print(f"🎯 Recovery Kernel Status")
        print(f"   Phase: {self.current_phase.value}")
        print(f"   Running: {'✅' if self.is_running else '❌'}")
        
        if self.recovery_state:
            self.state_registry.print_status()
        
        if self.security_manager:
            self.security_manager.print_security_status()
    
    async def shutdown(self) -> None:
        """Shutdown the Recovery Kernel"""
        print("🛑 Shutting down Recovery Kernel...")
        
        # Shutdown components
        if self.network_oracle:
            await self.network_oracle.shutdown()
        
        if self.security_manager:
            await self.security_manager.shutdown()
        
        if self.state_registry:
            # Final state save
            await self.state_registry.update_state(
                mission_active=False,
                current_phase="shutdown"
            )
        
        self.is_running = False
        print("✅ Recovery Kernel shutdown complete")
