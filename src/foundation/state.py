"""
PyPro Systems - Foundation State Registry
Persistent state management for recovery operations
"""

import json
import asyncio
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from enum import Enum

class BridgeStatus(Enum):
    """Bridge transaction status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    MINTED = "minted"
    FAILED = "failed"

class AccountStatus(Enum):
    """Account deployment status"""
    NOT_DEPLOYED = "not_deployed"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"

@dataclass
class BridgeTransaction:
    """Bridge transaction tracking"""
    tx_hash: str
    amount: float
    from_address: str
    to_address: str
    status: BridgeStatus
    timestamp: str
    block_number: Optional[int] = None
    l2_tx_hash: Optional[str] = None
    mint_timestamp: Optional[str] = None

@dataclass
class RecoveryState:
    """Complete recovery operation state"""
    # Mission identifiers
    phantom_address: str
    starknet_address: str
    
    # Bridge tracking
    bridge_transactions: List[BridgeTransaction]
    total_bridged: float
    
    # Account status
    account_status: AccountStatus
    account_tx_hash: Optional[str]
    
    # Balance tracking
    last_phantom_balance: float
    last_starknet_balance: float
    
    # Mission state
    mission_active: bool
    current_phase: str
    last_update: str
    
    # Security state
    security_unlocked: bool
    session_start: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "phantom_address": self.phantom_address,
            "starknet_address": self.starknet_address,
            "bridge_transactions": [asdict(tx) for tx in self.bridge_transactions],
            "total_bridged": self.total_bridged,
            "account_status": self.account_status.value,
            "account_tx_hash": self.account_tx_hash,
            "last_phantom_balance": self.last_phantom_balance,
            "last_starknet_balance": self.last_starknet_balance,
            "mission_active": self.mission_active,
            "current_phase": self.current_phase,
            "last_update": self.last_update,
            "security_unlocked": self.security_unlocked,
            "session_start": self.session_start
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecoveryState':
        """Create from dictionary"""
        bridge_transactions = [
            BridgeTransaction(**tx) for tx in data.get("bridge_transactions", [])
        ]
        
        return cls(
            phantom_address=data["phantom_address"],
            starknet_address=data["starknet_address"],
            bridge_transactions=bridge_transactions,
            total_bridged=data["total_bridged"],
            account_status=AccountStatus(data["account_status"]),
            account_tx_hash=data.get("account_tx_hash"),
            last_phantom_balance=data["last_phantom_balance"],
            last_starknet_balance=data["last_starknet_balance"],
            mission_active=data["mission_active"],
            current_phase=data["current_phase"],
            last_update=data["last_update"],
            security_unlocked=data["security_unlocked"],
            session_start=data["session_start"]
        )

class StateRegistry:
    """Persistent state registry for recovery operations"""
    
    def __init__(self, state_file: Optional[str] = None):
        self.state_file = Path(state_file or "data/recovery_state.json")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state: Optional[RecoveryState] = None
        self._lock = asyncio.Lock()
    
    async def initialize_state(self, phantom_address: str, starknet_address: str) -> RecoveryState:
        """Initialize new recovery state"""
        async with self._lock:
            self._state = RecoveryState(
                phantom_address=phantom_address,
                starknet_address=starknet_address,
                bridge_transactions=[],
                total_bridged=0.0,
                account_status=AccountStatus.NOT_DEPLOYED,
                account_tx_hash=None,
                last_phantom_balance=0.0,
                last_starknet_balance=0.0,
                mission_active=True,
                current_phase="initializing",
                last_update=datetime.now().isoformat(),
                security_unlocked=False,
                session_start=datetime.now().isoformat()
            )
            
            await self._save_state()
            return self._state
    
    async def load_state(self) -> Optional[RecoveryState]:
        """Load existing state from disk"""
        async with self._lock:
            try:
                if self.state_file.exists():
                    with open(self.state_file, 'r') as f:
                        data = json.load(f)
                    self._state = RecoveryState.from_dict(data)
                    return self._state
            except Exception as e:
                print(f"❌ Failed to load state: {e}")
            
            return None
    
    async def get_state(self) -> Optional[RecoveryState]:
        """Get current state"""
        async with self._lock:
            return self._state
    
    async def update_state(self, **updates) -> None:
        """Update state with new values"""
        async with self._lock:
            if not self._state:
                return
            
            for key, value in updates.items():
                if hasattr(self._state, key):
                    setattr(self._state, key, value)
            
            self._state.last_update = datetime.now().isoformat()
            await self._save_state()
    
    async def add_bridge_transaction(self, tx_hash: str, amount: float, from_address: str, to_address: str) -> None:
        """Add new bridge transaction to state"""
        async with self._lock:
            if not self._state:
                return
            
            bridge_tx = BridgeTransaction(
                tx_hash=tx_hash,
                amount=amount,
                from_address=from_address,
                to_address=to_address,
                status=BridgeStatus.PENDING,
                timestamp=datetime.now().isoformat()
            )
            
            self._state.bridge_transactions.append(bridge_tx)
            self._state.total_bridged += amount
            self._state.last_update = datetime.now().isoformat()
            
            await self._save_state()
    
    async def update_bridge_status(self, tx_hash: str, status: BridgeStatus, **kwargs) -> None:
        """Update bridge transaction status"""
        async with self._lock:
            if not self._state:
                return
            
            for tx in self._state.bridge_transactions:
                if tx.tx_hash == tx_hash:
                    tx.status = status
                    for key, value in kwargs.items():
                        if hasattr(tx, key):
                            setattr(tx, key, value)
                    break
            
            self._state.last_update = datetime.now().isoformat()
            await self._save_state()
    
    async def update_account_status(self, status: AccountStatus, tx_hash: Optional[str] = None) -> None:
        """Update account deployment status"""
        async with self._lock:
            if not self._state:
                return
            
            self._state.account_status = status
            if tx_hash:
                self._state.account_tx_hash = tx_hash
            
            self._state.last_update = datetime.now().isoformat()
            await self._save_state()
    
    async def update_balances(self, phantom_balance: float, starknet_balance: float) -> None:
        """Update balance information"""
        async with self._lock:
            if not self._state:
                return
            
            self._state.last_phantom_balance = phantom_balance
            self._state.last_starknet_balance = starknet_balance
            self._state.last_update = datetime.now().isoformat()
            
            await self._save_state()
    
    async def set_security_unlocked(self, unlocked: bool) -> None:
        """Set security unlock status"""
        async with self._lock:
            if not self._state:
                return
            
            self._state.security_unlocked = unlocked
            self._state.last_update = datetime.now().isoformat()
            
            await self._save_state()
    
    async def complete_mission(self) -> None:
        """Mark mission as completed"""
        async with self._lock:
            if not self._state:
                return
            
            self._state.mission_active = False
            self._state.current_phase = "completed"
            self._state.last_update = datetime.now().isoformat()
            
            await self._save_state()
    
    async def _save_state(self) -> None:
        """Save state to disk"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self._state.to_dict(), f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save state: {e}")
    
    def get_bridge_summary(self) -> Dict[str, Any]:
        """Get bridge transaction summary"""
        if not self._state:
            return {}
        
        pending = len([tx for tx in self._state.bridge_transactions if tx.status == BridgeStatus.PENDING])
        confirmed = len([tx for tx in self._state.bridge_transactions if tx.status == BridgeStatus.CONFIRMED])
        minted = len([tx for tx in self._state.bridge_transactions if tx.status == BridgeStatus.MINTED])
        failed = len([tx for tx in self._state.bridge_transactions if tx.status == BridgeStatus.FAILED])
        
        return {
            "total_transactions": len(self._state.bridge_transactions),
            "total_bridged": self._state.total_bridged,
            "pending": pending,
            "confirmed": confirmed,
            "minted": minted,
            "failed": failed
        }
    
    def print_status(self) -> None:
        """Print current status summary"""
        if not self._state:
            print("📂 No active recovery state")
            return
        
        print(f"📊 Recovery Status Report")
        print(f"   Phantom: {self._state.phantom_address}")
        print(f"   StarkNet: {self._state.starknet_address}")
        print(f"   Phase: {self._state.current_phase}")
        print(f"   Active: {'✅' if self._state.mission_active else '❌'}")
        print(f"   Security: {'🔓' if self._state.security_unlocked else '🔒'}")
        
        bridge_summary = self.get_bridge_summary()
        print(f"   Bridges: {bridge_summary.get('total_transactions', 0)} transactions")
        print(f"   Total Bridged: {bridge_summary.get('total_bridged', 0):.6f} ETH")
        print(f"   Account: {self._state.account_status.value}")
        
        if self._state.bridge_transactions:
            print(f"\n🔗 Bridge Transactions:")
            for i, tx in enumerate(self._state.bridge_transactions, 1):
                status_icon = {
                    BridgeStatus.PENDING: "⏳",
                    BridgeStatus.CONFIRMED: "✅",
                    BridgeStatus.MINTED: "🎯",
                    BridgeStatus.FAILED: "❌"
                }.get(tx.status, "❓")
                
                print(f"   {i}. {status_icon} {tx.amount:.6f} ETH - {tx.tx_hash[:10]}... ({tx.status.value})")
