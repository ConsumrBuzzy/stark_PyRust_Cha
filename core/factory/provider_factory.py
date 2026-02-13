#!/usr/bin/env python3
"""
Provider Factory - PhantomArbiter Pattern Implementation
Dynamically manages RPC providers with failover and health monitoring
Ported from PhantomArbiter/src/shared/system/ architecture
"""

import asyncio
import os
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from starknet_py.net.full_node_client import FullNodeClient
from loguru import logger
from rich.console import Console

class ProviderStatus(Enum):
    """Provider health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"

@dataclass
class ProviderConfig:
    """Configuration for a single RPC provider"""
    name: str
    url: str
    priority: int = 1
    timeout: float = 5.0
    max_retries: int = 3
    weight: float = 1.0
    enabled: bool = True

@dataclass
class ProviderMetrics:
    """Performance metrics for a provider"""
    status: ProviderStatus = ProviderStatus.UNKNOWN
    latency_ms: float = 0.0
    success_rate: float = 1.0
    last_success: float = 0.0
    last_error: str = ""
    total_requests: int = 0
    failed_requests: int = 0
    consecutive_failures: int = 0

class ProviderFactory:
    """
    Factory pattern for managing StarkNet RPC providers
    Based on PhantomArbiter's provider management architecture
    """
    
    def __init__(self):
        self.console = Console()
        self.providers: Dict[str, ProviderConfig] = {}
        self.metrics: Dict[str, ProviderMetrics] = {}
        self.clients: Dict[str, FullNodeClient] = {}
        self.load_environment()
        self.initialize_providers()
        
        logger.info(f"🏭 ProviderFactory initialized with {len(self.providers)} providers")
    
    def load_environment(self):
        """Load provider configurations from environment"""
        env_path = Path(__file__).parent.parent.parent / ".env"
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key.strip()] = value.strip()
    
    def initialize_providers(self):
        """Initialize provider configurations from environment"""
        
        # Primary providers with priorities
        provider_configs = [
            ProviderConfig(
                name="Alchemy",
                url=os.getenv("STARKNET_MAINNET_URL", ""),
                priority=1,
                weight=2.0  # Higher weight for primary provider
            ),
            ProviderConfig(
                name="Lava",
                url=os.getenv("STARKNET_LAVA_URL", ""),
                priority=2,
                weight=1.5
            ),
            ProviderConfig(
                name="1RPC",
                url=os.getenv("STARKNET_1RPC_URL", ""),
                priority=3,
                weight=1.0
            ),
            ProviderConfig(
                name="OnFinality",
                url=os.getenv("STARKNET_ONFINALITY_URL", ""),
                priority=4,
                weight=0.8
            ),
            ProviderConfig(
                name="BlastAPI",
                url=os.getenv("STARKNET_RPC_URL", ""),
                priority=5,
                weight=0.5
            )
        ]
        
        # Filter enabled providers with valid URLs
        for config in provider_configs:
            if config.url and config.enabled:
                self.providers[config.name] = config
                self.metrics[config.name] = ProviderMetrics()
                
                # Initialize client
                try:
                    self.clients[config.name] = FullNodeClient(
                        node_url=config.url,
                        timeout=config.timeout
                    )
                    logger.debug(f"✅ Initialized {config.name} client")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize {config.name}: {e}")
                    self.metrics[config.name].status = ProviderStatus.FAILED
                    self.metrics[config.name].last_error = str(e)
        
        logger.info(f"📊 Loaded {len(self.providers)} providers")
    
    async def health_check(self, provider_name: str) -> ProviderMetrics:
        """Perform health check on a specific provider"""
        
        if provider_name not in self.providers:
            return ProviderMetrics(status=ProviderStatus.FAILED, last_error="Provider not found")
        
        config = self.providers[provider_name]
        metrics = self.metrics[provider_name]
        
        start_time = time.time()
        
        try:
            client = self.clients[provider_name]
            
            # Test basic connectivity with block number
            block_number = await client.get_block_number()
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Update metrics
            metrics.status = ProviderStatus.HEALTHY
            metrics.latency_ms = latency_ms
            metrics.last_success = time.time()
            metrics.consecutive_failures = 0
            metrics.total_requests += 1
            
            # Update success rate
            if metrics.total_requests > 0:
                metrics.success_rate = (metrics.total_requests - metrics.failed_requests) / metrics.total_requests
            
            logger.debug(f"✅ {provider_name} health check passed: {latency_ms:.2f}ms")
            
        except Exception as e:
            # Update failure metrics
            metrics.status = ProviderStatus.FAILED
            metrics.last_error = str(e)[:50]
            metrics.consecutive_failures += 1
            metrics.total_requests += 1
            metrics.failed_requests += 1
            
            # Update success rate
            if metrics.total_requests > 0:
                metrics.success_rate = (metrics.total_requests - metrics.failed_requests) / metrics.total_requests
            
            # Degrade after multiple failures
            if metrics.consecutive_failures >= 3:
                metrics.status = ProviderStatus.DEGRADED
            
            logger.warning(f"❌ {provider_name} health check failed: {e}")
        
        return metrics
    
    async def check_all_providers(self) -> Dict[str, ProviderMetrics]:
        """Perform health checks on all providers"""
        
        logger.info("🔍 Performing health checks on all providers...")
        
        # Parallel health checks
        tasks = [
            self.health_check(name) 
            for name in self.providers.keys()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update metrics
        for i, name in enumerate(self.providers.keys()):
            if not isinstance(results[i], Exception):
                self.metrics[name] = results[i]
        
        return self.metrics
    
    def get_best_provider(self) -> Tuple[str, FullNodeClient]:
        """Get the best available provider based on metrics"""
        
        # Filter healthy providers
        healthy_providers = [
            (name, config, metrics) 
            for name, config, metrics in [
                (name, self.providers[name], self.metrics[name]) 
                for name in self.providers.keys()
            ]
            if metrics.status == ProviderStatus.HEALTHY
        ]
        
        if not healthy_providers:
            # Fallback to degraded providers
            healthy_providers = [
                (name, config, metrics) 
                for name, config, metrics in [
                    (name, self.providers[name], self.metrics[name]) 
                    for name in self.providers.keys()
                ]
                if metrics.status == ProviderStatus.DEGRADED
            ]
        
        if not healthy_providers:
            raise RuntimeError("No healthy providers available")
        
        # Sort by priority, weight, and success rate
        def sort_key(item):
            name, config, metrics = item
            return (
                -config.priority,  # Higher priority first
                -config.weight,    # Higher weight first
                -metrics.success_rate,  # Higher success rate first
                metrics.latency_ms  # Lower latency first
            )
        
        healthy_providers.sort(key=sort_key)
        best_name, best_config, best_metrics = healthy_providers[0]
        
        logger.debug(f"🎯 Selected best provider: {best_name} (priority: {best_config.priority}, success_rate: {best_metrics.success_rate:.2f})")
        
        return best_name, self.clients[best_name]
    
    async def execute_with_failover(self, operation, *args, **kwargs):
        """Execute operation with automatic failover"""
        
        last_exception = None
        
        # Try providers in order of preference
        for attempt in range(len(self.providers)):
            try:
                provider_name, client = self.get_best_provider()
                logger.debug(f"🔄 Attempting operation with {provider_name} (attempt {attempt + 1})")
                
                # Execute the operation
                result = await operation(client, *args, **kwargs)
                
                # Mark success
                self.metrics[provider_name].last_success = time.time()
                self.metrics[provider_name].consecutive_failures = 0
                
                return result
                
            except Exception as e:
                last_exception = e
                provider_name, _ = self.get_best_provider()
                
                # Mark failure
                self.metrics[provider_name].consecutive_failures += 1
                self.metrics[provider_name].failed_requests += 1
                self.metrics[provider_name].total_requests += 1
                
                # Update status if needed
                if self.metrics[provider_name].consecutive_failures >= 3:
                    self.metrics[provider_name].status = ProviderStatus.DEGRADED
                
                logger.warning(f"⚠️ Operation failed with {provider_name}: {e}")
                
                # Continue to next provider
                continue
        
        # All providers failed
        logger.error(f"❌ Operation failed with all providers: {last_exception}")
        raise last_exception
    
    def create_status_table(self) -> Any:
        """Create rich table showing provider status"""
        from rich.table import Table
        
        table = Table(title="🏭 Provider Factory Status")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Latency", justify="right")
        table.add_column("Success Rate", justify="right")
        table.add_column("Priority", justify="right")
        table.add_column("Weight", justify="right")
        table.add_column("Last Error", style="dim")
        
        for name in sorted(self.providers.keys()):
            config = self.providers[name]
            metrics = self.metrics[name]
            
            # Status styling
            status_color = {
                ProviderStatus.HEALTHY: "green",
                ProviderStatus.DEGRADED: "yellow",
                ProviderStatus.FAILED: "red",
                ProviderStatus.UNKNOWN: "dim"
            }.get(metrics.status, "white")
            
            table.add_row(
                name,
                f"[{status_color}]{metrics.status.value}[/{status_color}]",
                f"{metrics.latency_ms:.1f}ms" if metrics.latency_ms > 0 else "N/A",
                f"{metrics.success_rate:.1%}",
                str(config.priority),
                str(config.weight),
                metrics.last_error[:20] if metrics.last_error else ""
            )
        
        return table
    
    async def start_health_monitoring(self, interval: int = 60):
        """Start continuous health monitoring"""
        
        logger.info(f"🔄 Starting health monitoring (interval: {interval}s)")
        
        while True:
            try:
                await self.check_all_providers()
                
                # Log summary
                healthy_count = sum(1 for m in self.metrics.values() if m.status == ProviderStatus.HEALTHY)
                total_count = len(self.metrics)
                
                logger.info(f"📊 Health check complete: {healthy_count}/{total_count} providers healthy")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
                await asyncio.sleep(interval)
    
    def get_factory_summary(self) -> Dict[str, Any]:
        """Get comprehensive factory summary"""
        
        healthy_count = sum(1 for m in self.metrics.values() if m.status == ProviderStatus.HEALTHY)
        degraded_count = sum(1 for m in self.metrics.values() if m.status == ProviderStatus.DEGRADED)
        failed_count = sum(1 for m in self.metrics.values() if m.status == ProviderStatus.FAILED)
        
        avg_success_rate = sum(m.success_rate for m in self.metrics.values()) / len(self.metrics) if self.metrics else 0
        avg_latency = sum(m.latency_ms for m in self.metrics.values() if m.latency_ms > 0) / sum(1 for m in self.metrics.values() if m.latency_ms > 0) if any(m.latency_ms > 0 for m in self.metrics.values()) else 0
        
        return {
            "total_providers": len(self.providers),
            "healthy_providers": healthy_count,
            "degraded_providers": degraded_count,
            "failed_providers": failed_count,
            "average_success_rate": avg_success_rate,
            "average_latency_ms": avg_latency,
            "factory_status": "operational" if healthy_count > 0 else "failed"
        }

# Global factory instance
_provider_factory: Optional[ProviderFactory] = None

def get_provider_factory() -> ProviderFactory:
    """Get global provider factory instance"""
    global _provider_factory
    if _provider_factory is None:
        _provider_factory = ProviderFactory()
    return _provider_factory

async def initialize_factory():
    """Initialize the global provider factory"""
    factory = get_provider_factory()
    await factory.check_all_providers()
    return factory
