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
from ..foundation.security import EncryptedSigner
from ..foundation.network import NetworkOracle
from ..foundation.state import PersistentState

class RecoveryState(Enum):
    """Recovery state machine states"""
    INITIALIZING = "initializing"
    SECURITY_UNLOCKED = "security_unlocked"
    REFUEL_PENDING = "refuel_pending"
    REFUEL_IN_PROGRESS = "refuel_in_progress"
    REFUEL_COMPLETE = "refuel_complete"
    MINT_PENDING = "mint_pending"
    MINT_COMPLETE = "mint_complete"
    ACTIVATION_PENDING = "activation_pending"
    ACTIVATION_COMPLETE = "activation_complete"
    MISSION_SUCCESS = "mission_success"
    MISSION_FAILED = "mission_failed"

@dataclass
class RecoveryContext:
    """Recovery execution context"""
    phantom_address: str
    starknet_address: str
    master_password: Optional[str] = None
    private_key_unlocked: bool = False
    
    # Bridge tracking
    bridge_transactions: List[Dict[str, Any]] = field(default_factory=list)
    total_bridged: float = 0.0
    
    # Balance tracking
    phantom_balance: float = 0.0
    starknet_balance: float = 0.0
    
    # State tracking
    current_state: RecoveryState = RecoveryState.INITIALIZING
    state_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Configuration
    activation_threshold: float = ACTIVATION_THRESHOLD
    gas_reserve: float = GAS_RESERVE
    max_bridge_attempts: int = 3

class RecoveryKernel:
    """Unified Recovery Kernel - Single Source of Truth"""
    
    def __init__(self, phantom_address: str, starknet_address: str):
        self.context = RecoveryContext(
            phantom_address=phantom_address,
            starknet_address=starknet_address
        )
        
        # Core components
        self.security_vault: Optional[EncryptedSigner] = None
        self.network_oracle: Optional[NetworkOracle] = None
        self.persistent_state: Optional[PersistentState] = None
        
        # State machine
        self.is_running = False
        self.state_handlers = {
            RecoveryState.INITIALIZING: self._handle_initializing,
            RecoveryState.SECURITY_UNLOCKED: self._handle_security_unlocked,
            RecoveryState.REFUEL_PENDING: self._handle_refuel_pending,
            RecoveryState.REFUEL_IN_PROGRESS: self._handle_refuel_in_progress,
            RecoveryState.REFUEL_COMPLETE: self._handle_refuel_complete,
            RecoveryState.MINT_PENDING: self._handle_mint_pending,
            RecoveryState.MINT_COMPLETE: self._handle_mint_complete,
            RecoveryState.ACTIVATION_PENDING: self._handle_activation_pending,
            RecoveryState.ACTIVATION_COMPLETE: self._handle_activation_complete,
            RecoveryState.MISSION_SUCCESS: self._handle_mission_success,
            RecoveryState.MISSION_FAILED: self._handle_mission_failed,
        }
    
    async def initialize(self) -> bool:
        """Initialize the Recovery Kernel"""
        print("🚀 Initializing Recovery Kernel...")
        
        try:
            # Initialize persistent state
            self.persistent_state = PersistentState()
            await self.persistent_state.load()
            
            # Load previous context if exists
            saved_context = await self.persistent_state.get_context()
            if saved_context:
                self.context = saved_context
                print(f"📂 Loaded previous context: {self.context.current_state.value}")
            
            # Initialize Network Oracle
            self.network_oracle = NetworkOracle()
            if not await self.network_oracle.initialize():
                print("❌ Failed to initialize Network Oracle")
                return False
            
            # Initialize Security Vault
            self.security_vault = EncryptedSigner()
            
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
            while self.is_running and self.context.current_state not in [
                RecoveryState.MISSION_SUCCESS, 
                RecoveryState.MISSION_FAILED
            ]:
                # Get current state handler
                handler = self.state_handlers.get(self.context.current_state)
                if not handler:
                    print(f"❌ No handler for state: {self.context.current_state}")
                    await self._transition_to(RecoveryState.MISSION_FAILED)
                    continue
                
                # Execute state handler
                print(f"🔄 Executing state: {self.context.current_state.value}")
                await handler()
                
                # Save state
                await self._save_state()
                
                # Brief pause between states
                await asyncio.sleep(1)
            
            return self.context.current_state == RecoveryState.MISSION_SUCCESS
            
        except Exception as e:
            print(f"❌ Recovery execution failed: {e}")
            await self._transition_to(RecoveryState.MISSION_FAILED)
            return False
    
    async def _transition_to(self, new_state: RecoveryState, message: str = "") -> None:
        """Transition to a new state"""
        old_state = self.context.current_state
        self.context.current_state = new_state
        
        # Log transition
        transition = {
            "timestamp": datetime.now().isoformat(),
            "from": old_state.value,
            "to": new_state.value,
            "message": message
        }
        self.context.state_history.append(transition)
        
        print(f"🔄 State transition: {old_state.value} → {new_state.value}")
        if message:
            print(f"   📝 {message}")
    
    async def _save_state(self) -> None:
        """Save current state to persistent storage"""
        if self.persistent_state:
            await self.persistent_state.save_context(self.context)
    
    # State Handlers
    async def _handle_initializing(self) -> None:
        """Handle initializing state"""
        await self._transition_to(RecoveryState.SECURITY_UNLOCKED, "Ready for security unlock")
    
    async def _handle_security_unlocked(self) -> None:
        """Handle security unlocked state"""
        if not self.context.private_key_unlocked:
            print("🔐 Security vault locked - prompting for password")
            # This would trigger password prompt
            return
        
        await self._transition_to(RecoveryState.REFUEL_PENDING, "Security unlocked, ready for refuel")
    
    async def _handle_refuel_pending(self) -> None:
        """Handle refuel pending state"""
        # Check Phantom balance
        phantom_balance = await self.network_oracle.get_balance(self.context.phantom_address, "base")
        self.context.phantom_balance = phantom_balance
        
        print(f"💰 Phantom balance: {phantom_balance:.6f} ETH")
        
        if phantom_balance > self.context.gas_reserve:
            await self._transition_to(RecoveryState.REFUEL_IN_PROGRESS, "Sufficient balance for refuel")
        else:
            print(f"❌ Insufficient balance: {phantom_balance:.6f} ETH <= {self.context.gas_reserve:.6f} ETH")
            await self._transition_to(RecoveryState.MISSION_FAILED, "Insufficient Phantom balance")
    
    async def _handle_refuel_in_progress(self) -> None:
        """Handle refuel in progress state"""
        # Calculate bridge amount (zero-waste)
        bridge_amount = max(0, self.context.phantom_balance - self.context.gas_reserve)
        
        print(f"🌉 Executing bridge: {bridge_amount:.6f} ETH")
        
        # Execute bridge
        bridge_result = await self.network_oracle.execute_bridge(
            self.context.phantom_address,
            self.context.starknet_address,
            bridge_amount
        )
        
        if bridge_result.get("success"):
            # Track transaction
            self.context.bridge_transactions.append({
                "tx_hash": bridge_result["tx_hash"],
                "amount": bridge_amount,
                "timestamp": datetime.now().isoformat()
            })
            self.context.total_bridged += bridge_amount
            
            await self._transition_to(RecoveryState.REFUEL_COMPLETE, f"Bridge successful: {bridge_amount:.6f} ETH")
        else:
            print(f"❌ Bridge failed: {bridge_result.get('error')}")
            await self._transition_to(RecoveryState.MISSION_FAILED, "Bridge execution failed")
    
    async def _handle_refuel_complete(self) -> None:
        """Handle refuel complete state"""
        await self._transition_to(RecoveryState.MINT_PENDING, "Bridge complete, waiting for mint")
    
    async def _handle_mint_pending(self) -> None:
        """Handle mint pending state"""
        # Check StarkNet balance
        starknet_balance = await self.network_oracle.get_balance(self.context.starknet_address, "starknet")
        self.context.starknet_balance = starknet_balance
        
        print(f"💰 StarkNet balance: {starknet_balance:.6f} ETH")
        
        if starknet_balance >= self.context.activation_threshold:
            await self._transition_to(RecoveryState.MINT_COMPLETE, f"Mint complete: {starknet_balance:.6f} ETH")
        else:
            needed = self.context.activation_threshold - starknet_balance
            print(f"⏳ Need {needed:.6f} more ETH")
            # Stay in this state and keep checking
    
    async def _handle_mint_complete(self) -> None:
        """Handle mint complete state"""
        await self._transition_to(RecoveryState.ACTIVATION_PENDING, "Mint complete, ready for activation")
    
    async def _handle_activation_pending(self) -> None:
        """Handle activation pending state"""
        print("⚛️ Executing account activation...")
        
        # Get private key from security vault
        private_key = await self.security_vault.get_private_key()
        
        # Execute activation
        activation_result = await self.network_oracle.activate_account(
            self.context.starknet_address,
            private_key
        )
        
        if activation_result.get("success"):
            await self._transition_to(RecoveryState.ACTIVATION_COMPLETE, "Account activation successful")
        else:
            print(f"❌ Activation failed: {activation_result.get('error')}")
            await self._transition_to(RecoveryState.MISSION_FAILED, "Account activation failed")
    
    async def _handle_activation_complete(self) -> None:
        """Handle activation complete state"""
        await self._transition_to(RecoveryState.MISSION_SUCCESS, "Mission completed successfully")
    
    async def _handle_mission_success(self) -> None:
        """Handle mission success state"""
        print("🎉 MISSION SUCCESS!")
        print(f"💰 Total bridged: {self.context.total_bridged:.6f} ETH")
        print(f"⚛️ Account activated: {self.context.starknet_address}")
        self.is_running = False
    
    async def _handle_mission_failed(self) -> None:
        """Handle mission failed state"""
        print("❌ MISSION FAILED!")
        self.is_running = False
    
    async def unlock_security(self, password: str) -> bool:
        """Unlock security vault"""
        if not self.security_vault:
            return False
        
        try:
            success = await self.security_vault.unlock(password)
            if success:
                self.context.master_password = password
                self.context.private_key_unlocked = True
                await self._transition_to(RecoveryState.REFUEL_PENDING, "Security vault unlocked")
                return True
            else:
                print("❌ Invalid password")
                return False
        except Exception as e:
            print(f"❌ Security unlock failed: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the Recovery Kernel"""
        print("🛑 Shutting down Recovery Kernel...")
        
        # Save final state
        await self._save_state()
        
        # Shutdown components
        if self.network_oracle:
            await self.network_oracle.shutdown()
        
        if self.persistent_state:
            await self.persistent_state.close()
        
        self.is_running = False
        print("✅ Recovery Kernel shutdown complete")
