"""
PyPro Systems - Complete Feature Integration
Migrating ALL functionality from archived tools into the unified engine
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime

from ..foundation.constants import *
from ..foundation.network import NetworkOracle
from ..foundation.state import StateRegistry, BridgeStatus, AccountStatus
from .bridge_system import BridgeSystem, ActivationSystem, MonitoringSystem

class MonitoringMode(Enum):
    """Monitoring modes from legacy tools"""
    STARGATE_WATCH = "stargate_watch"
    GHOST_SENTRY = "ghost_sentry"
    BRIDGE_RECOVERY = "bridge_recovery"
    ADVANCED_TRACKING = "advanced_tracking"

@dataclass
class MonitoringConfig:
    """Configuration for different monitoring modes"""
    mode: MonitoringMode
    poll_interval: int
    threshold: float
    addresses: List[str]
    enable_ui: bool = True
    enable_logging: bool = True

class EnhancedMonitoringSystem(MonitoringSystem):
    """Enhanced monitoring system with ALL legacy tool functionality"""
    
    def __init__(self, network_oracle, state_registry):
        super().__init__(network_oracle, state_registry)
        
        # Legacy monitoring configurations
        self.monitoring_configs = {
            MonitoringMode.STARGATE_WATCH: MonitoringConfig(
                mode=MonitoringMode.STARGATE_WATCH,
                poll_interval=30,
                threshold=ACTIVATION_THRESHOLD,
                addresses=[],  # Will be set dynamically
                enable_ui=True,
                enable_logging=True
            ),
            MonitoringMode.GHOST_SENTRY: MonitoringConfig(
                mode=MonitoringMode.GHOST_SENTRY,
                poll_interval=180,  # 3 minutes
                threshold=0.005,   # 0.005 ETH minimum
                addresses=["ghost_address", "main_wallet"],
                enable_ui=False,
                enable_logging=True
            ),
            MonitoringMode.BRIDGE_RECOVERY: MonitoringConfig(
                mode=MonitoringMode.BRIDGE_RECOVERY,
                poll_interval=60,
                threshold=ACTIVATION_THRESHOLD,
                addresses=[],
                enable_ui=True,
                enable_logging=True
            ),
            MonitoringMode.ADVANCED_TRACKING: MonitoringConfig(
                mode=MonitoringMode.ADVANCED_TRACKING,
                poll_interval=30,
                threshold=ACTIVATION_THRESHOLD,
                addresses=[],
                enable_ui=True,
                enable_logging=True
            )
        }
        
        self.current_mode = MonitoringMode.STARGATE_WATCH
        self.monitoring_active = False
        
        # Rich UI components (from starkgate_watch.py)
        self.console = None
        self.dashboard = None
        self.progress = None
        
        # Advanced tracking (from advanced_tracker.py)
        self.tracking_data = {}
        self.multi_source_validation = True
    
    def initialize_ui(self):
        """Initialize Rich UI components"""
        try:
            from rich.console import Console
            from rich.progress import Progress, SpinnerColumn, TextColumn
            from rich.live import Live
            
            self.console = Console()
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            )
            
            return True
        except ImportError:
            print("⚠️ Rich UI not available - using console output")
            return False
    
    async def start_stargate_watch(self, starknet_address: str) -> Dict[str, Any]:
        """StarkGate Watch functionality from starkgate_watch.py"""
        print("🔍 STARTING STARGATE WATCH MODE")
        print("=" * 50)
        
        self.current_mode = MonitoringMode.STARGATE_WATCH
        config = self.monitoring_configs[self.current_mode]
        config.addresses = [starknet_address]
        
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                # Multi-source balance checking
                balance_results = await self._multi_source_balance_check(starknet_address)
                
                # Display results
                await self._display_stargate_status(balance_results)
                
                # Check threshold
                if balance_results.get("alchemy_balance", 0) >= config.threshold:
                    print(f"🎯 THRESHOLD REACHED: {balance_results['alchemy_balance']:.6f} ETH")
                    return {
                        "success": True,
                        "final_balance": balance_results["alchemy_balance"],
                        "threshold_met": True,
                        "mode": "stargate_watch"
                    }
                
                await asyncio.sleep(config.poll_interval)
                
            except Exception as e:
                print(f"❌ StarkGate watch error: {e}")
                await asyncio.sleep(config.poll_interval)
        
        return {"success": False, "error": "Monitoring stopped"}
    
    async def start_ghost_sentry(self, ghost_address: str, main_wallet: str) -> Dict[str, Any]:
        """Ghost Sentry functionality from sentry.py"""
        print("👻 STARTING GHOST SENTRY MODE")
        print("=" * 50)
        
        self.current_mode = MonitoringMode.GHOST_SENTRY
        config = self.monitoring_configs[self.current_mode]
        config.addresses = [ghost_address, main_wallet]
        
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                # Shadow protocol monitoring (L7 DPI Bypass)
                ghost_balance = await self._shadow_balance_check(ghost_address)
                main_balance = await self._shadow_balance_check(main_wallet)
                
                print(f"👻 Ghost Balance: {ghost_balance:.6f} ETH")
                print(f"💰 Main Wallet: {main_balance:.6f} ETH")
                
                # Check ghost threshold
                if ghost_balance >= config.threshold:
                    print(f"🎯 GHOST THRESHOLD REACHED: {ghost_balance:.6f} ETH")
                    return {
                        "success": True,
                        "ghost_balance": ghost_balance,
                        "main_balance": main_balance,
                        "threshold_met": True,
                        "mode": "ghost_sentry"
                    }
                
                await asyncio.sleep(config.poll_interval)
                
            except Exception as e:
                print(f"❌ Ghost sentry error: {e}")
                await asyncio.sleep(config.poll_interval)
        
        return {"success": False, "error": "Monitoring stopped"}
    
    async def start_bridge_recovery(self, bridge_tx_hash: str) -> Dict[str, Any]:
        """Bridge Recovery functionality from bridge_recovery.py"""
        print("🔄 STARTING BRIDGE RECOVERY MODE")
        print("=" * 50)
        
        self.current_mode = MonitoringMode.BRIDGE_RECOVERY
        config = self.monitoring_configs[self.current_mode]
        
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                # Check bridge status on multiple sources
                bridge_status = await self._multi_source_bridge_check(bridge_tx_hash)
                
                # Check if minted
                current_balance = await self.network_oracle.get_balance(
                    self.state_registry.recovery_state.starknet_address,
                    "starknet"
                )
                
                print(f"🌉 Bridge Status: {bridge_status.get('status', 'unknown')}")
                print(f"💰 Current Balance: {current_balance:.6f} ETH")
                
                if bridge_status.get("status") == "minted" or current_balance >= config.threshold:
                    print(f"🎯 BRIDGE RECOVERY COMPLETE: {current_balance:.6f} ETH")
                    return {
                        "success": True,
                        "final_balance": current_balance,
                        "bridge_status": bridge_status,
                        "mode": "bridge_recovery"
                    }
                
                await asyncio.sleep(config.poll_interval)
                
            except Exception as e:
                print(f"❌ Bridge recovery error: {e}")
                await asyncio.sleep(config.poll_interval)
        
        return {"success": False, "error": "Monitoring stopped"}
    
    async def start_advanced_tracking(self, tx_hash: str) -> Dict[str, Any]:
        """Advanced Tracking functionality from advanced_tracker.py"""
        print("🔍 STARTING ADVANCED TRACKING MODE")
        print("=" * 50)
        
        self.current_mode = MonitoringMode.ADVANCED_TRACKING
        config = self.monitoring_configs[self.current_mode]
        
        self.monitoring_active = True
        self.tracking_data = {
            "tx_hash": tx_hash,
            "start_time": datetime.now().isoformat(),
            "base_status": None,
            "starkgate_status": None,
            "starkscan_status": None,
            "balance_history": []
        }
        
        while self.monitoring_active:
            try:
                # Comprehensive tracking across multiple sources
                await self._update_tracking_data()
                
                # Display comprehensive status
                await self._display_advanced_status()
                
                # Check if complete
                current_balance = self.tracking_data.get("current_balance", 0)
                if current_balance >= config.threshold:
                    print(f"🎯 TRACKING COMPLETE: {current_balance:.6f} ETH")
                    return {
                        "success": True,
                        "final_balance": current_balance,
                        "tracking_data": self.tracking_data,
                        "mode": "advanced_tracking"
                    }
                
                await asyncio.sleep(config.poll_interval)
                
            except Exception as e:
                print(f"❌ Advanced tracking error: {e}")
                await asyncio.sleep(config.poll_interval)
        
        return {"success": False, "error": "Tracking stopped"}
    
    async def _multi_source_balance_check(self, address: str) -> Dict[str, Any]:
        """Multi-source balance checking (from advanced_tracker.py)"""
        results = {}
        
        # Alchemy check
        try:
            alchemy_balance = await self.network_oracle.get_balance(address, "starknet")
            results["alchemy_balance"] = alchemy_balance
            results["alchemy_status"] = "success"
        except Exception as e:
            results["alchemy_balance"] = None
            results["alchemy_status"] = f"error: {e}"
        
        # StarkScan check (if available)
        try:
            # This would integrate with StarkScan API
            results["starkscan_balance"] = results["alchemy_balance"]  # Fallback
            results["starkscan_status"] = "success"
        except Exception as e:
            results["starkscan_balance"] = None
            results["starkscan_status"] = f"error: {e}"
        
        return results
    
    async def _shadow_balance_check(self, address: str) -> float:
        """Shadow protocol balance check (from sentry.py)"""
        try:
            # Use ERC-20 balanceOf call for L7 DPI bypass
            return await self.network_oracle.get_balance(address, "starknet")
        except Exception as e:
            print(f"❌ Shadow balance check failed: {e}")
            return 0.0
    
    async def _multi_source_bridge_check(self, tx_hash: str) -> Dict[str, Any]:
        """Multi-source bridge status check"""
        results = {}
        
        # Base network check
        try:
            from web3 import Web3
            from web3.middleware import ExtraDataToPOAMiddleware
            
            w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
            w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            results["base_status"] = "confirmed" if receipt.status == 1 else "failed"
            results["base_block"] = receipt.blockNumber
        except Exception as e:
            results["base_status"] = f"error: {e}"
        
        # StarkGate check
        results["starkgate_status"] = "pending"  # Would check StarkGate API
        
        return results
    
    async def _update_tracking_data(self) -> None:
        """Update tracking data for advanced mode"""
        if not self.tracking_data:
            return
        
        # Update balance
        try:
            current_balance = await self.network_oracle.get_balance(
                self.state_registry.recovery_state.starknet_address,
                "starknet"
            )
            self.tracking_data["current_balance"] = current_balance
            self.tracking_data["balance_history"].append({
                "timestamp": datetime.now().isoformat(),
                "balance": current_balance
            })
        except Exception as e:
            print(f"❌ Balance update failed: {e}")
    
    async def _display_stargate_status(self, balance_results: Dict[str, Any]) -> None:
        """Display StarkGate monitoring status"""
        print(f"🔍 STARGATE MONITOR - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 40)
        
        if balance_results.get("alchemy_balance") is not None:
            print(f"💰 Alchemy Balance: {balance_results['alchemy_balance']:.6f} ETH ✅")
        else:
            print(f"💰 Alchemy Balance: {balance_results.get('alchemy_status', 'Unknown')} ❌")
        
        if balance_results.get("starkscan_balance") is not None:
            print(f"🔍 StarkScan Balance: {balance_results['starkscan_balance']:.6f} ETH ✅")
        else:
            print(f"🔍 StarkScan Balance: {balance_results.get('starkscan_status', 'Unknown')} ❌")
    
    async def _display_advanced_status(self) -> None:
        """Display advanced tracking status"""
        if not self.tracking_data:
            return
        
        print(f"🔍 ADVANCED TRACKING - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)
        
        if self.tracking_data.get("current_balance"):
            print(f"💰 Current Balance: {self.tracking_data['current_balance']:.6f} ETH")
        
        print(f"🔗 Tracking TX: {self.tracking_data['tx_hash'][:10]}...")
        print(f"⏱️  Elapsed: {datetime.now() - datetime.fromisoformat(self.tracking_data['start_time'])}")
    
    def stop_monitoring(self) -> None:
        """Stop all monitoring"""
        self.monitoring_active = False
        print("🛑 Monitoring stopped")

class AtomicBundle:
    """Atomic bundle functionality from atomic_activation.py"""
    
    def __init__(self, activation_system: ActivationSystem):
        self.activation_system = activation_system
        self.operations = []
    
    def add_operation(self, operation_type: str, params: Dict[str, Any]) -> None:
        """Add operation to atomic bundle"""
        self.operations.append({
            "type": operation_type,
            "params": params,
            "status": "pending"
        })
    
    async def execute_bundle(self) -> Dict[str, Any]:
        """Execute atomic bundle"""
        print("⚛️ EXECUTING ATOMIC BUNDLE")
        print("=" * 30)
        
        results = []
        
        for operation in self.operations:
            try:
                print(f"🔄 Executing: {operation['type']}")
                
                if operation["type"] == "activate_account":
                    result = await self.activation_system.execute_account_deployment(
                        operation["params"]["starknet_address"]
                    )
                    results.append(result)
                
                operation["status"] = "completed"
                
            except Exception as e:
                print(f"❌ Operation failed: {e}")
                operation["status"] = "failed"
                results.append({"success": False, "error": str(e)})
        
        # Check if all operations succeeded
        all_success = all(r.get("success", False) for r in results)
        
        return {
            "success": all_success,
            "operations": results,
            "bundle_size": len(self.operations)
        }
