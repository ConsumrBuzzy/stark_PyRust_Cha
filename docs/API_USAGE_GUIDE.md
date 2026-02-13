# API Usage Guide - StarkNet Influence Automation

## Overview

This guide provides comprehensive API documentation for the StarkNet Influence automation system. The API is organized into several core modules that handle different aspects of blockchain operations and game automation.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    API Architecture                        │
├─────────────────────────────────────────────────────────────┤
│  Core Engines                                               │
│  ├── RecoveryKernel     │  ├── InfluenceStrategy           │
│  ├── BridgeSystem       │  ├── NetworkOracle               │
│  ├── SecurityManager    │  ├── StateRegistry               │
│  └── MonitoringSystem   │  └── ReportingSystem             │
├─────────────────────────────────────────────────────────────┤
│  Foundation Layer                                            │
│  ├── Network Management │  ├── Security & Encryption       │
│  ├── State Persistence  │  ├── Configuration Management     │
│  └── Logging & Reporting│  └── Error Handling              │
├─────────────────────────────────────────────────────────────┤
│  External Integrations                                       │
│  ├── StarkNet RPC       │  ├── Base Network                 │
│  ├── Influence Game API │  ├── Bridge Contracts             │
│  └── Notification Services│ └── Market Data Feeds            │
└─────────────────────────────────────────────────────────────┘
```

## Core API Modules

### 1. RecoveryKernel API

**Purpose**: Unified state machine for account recovery and deployment operations.

#### Initialization

```python
from src.engines.recovery_kernel import RecoveryKernel

# Create kernel instance
kernel = RecoveryKernel(
    phantom_address: str,      # Phantom wallet address on Base
    starknet_address: str      # StarkNet wallet address
)

# Initialize async components
await kernel.initialize()
```

#### Core Methods

##### `execute_full_auto() -> bool`
**Description**: Execute complete automated recovery mission
**Returns**: Success status
**Usage**:
```python
success = await kernel.execute_full_auto()
if success:
    print("Recovery completed successfully")
else:
    print("Recovery failed")
```

##### `execute_recovery() -> bool`
**Description**: Execute step-by-step recovery with manual control
**Returns**: Success status
**Usage**:
```python
# Manual control over each phase
await kernel.initialize()
await kernel.unlock_security(password="your_password")
success = await kernel.execute_recovery()
```

##### `unlock_security(password: str) -> bool`
**Description**: Unlock encrypted security vault
**Parameters**:
- `password`: Vault encryption password
**Returns**: Unlock success status
**Usage**:
```python
unlocked = await kernel.unlock_security("secure_password")
if unlocked:
    print("Security vault unlocked")
```

##### `check_gas_safety() -> bool`
**Description**: Verify gas prices are within safe limits
**Returns**: Gas safety status
**Usage**:
```python
if await kernel.check_gas_safety():
    print("Gas prices safe for automation")
else:
    print("Gas prices too high - aborting")
```

#### Phase Management

```python
from src.engines.recovery_kernel import RecoveryPhase

# Check current phase
current_phase = kernel.current_phase
print(f"Current phase: {current_phase.value}")

# Manual phase transitions (advanced usage)
await kernel._transition_to(
    RecoveryPhase.BRIDGE_EXECUTING,
    "Manual transition for testing"
)
```

#### Status Monitoring

```python
# Print comprehensive status
kernel.print_status()

# Get specific state information
if kernel.recovery_state:
    bridges = kernel.recovery_state.bridge_transactions
    balance = kernel.recovery_state.last_phantom_balance
```

### 2. NetworkOracle API

**Purpose**: Unified blockchain network management and operations.

#### Initialization

```python
from src.foundation.network import NetworkOracle

oracle = NetworkOracle()
await oracle.initialize()
```

#### Core Methods

##### `get_balance(address: str, network: str) -> float`
**Description**: Get ETH balance for address on specified network
**Parameters**:
- `address`: Wallet address to check
- `network`: Network name ("base" or "starknet")
**Returns**: Balance in ETH
**Usage**:
```python
phantom_balance = await oracle.get_balance(
    "0x1234...", "base"
)
starknet_balance = await oracle.get_balance(
    "0x5678...", "starknet"
)
```

##### `execute_bridge(from_address: str, to_address: str, amount: float) -> Dict[str, Any]`
**Description**: Execute StarkGate bridge transaction
**Parameters**:
- `from_address`: Source Phantom wallet address
- `to_address`: Target StarkNet address
- `amount`: Amount to bridge in ETH
**Returns**: Transaction result dictionary
**Usage**:
```python
result = await oracle.execute_bridge(
    "0x1234...", "0x5678...", 0.1
)

if result["success"]:
    print(f"Bridge successful: {result['tx_hash']}")
else:
    print(f"Bridge failed: {result['error']}")
```

##### `activate_account(starknet_address: str, private_key: str) -> Dict[str, Any]`
**Description**: Deploy and activate StarkNet account
**Parameters**:
- `starknet_address`: Target StarkNet address
- `private_key`: Private key for signing
**Returns**: Activation result dictionary
**Usage**:
```python
result = await oracle.activate_account(
    "0x5678...", "0xabcdef..."
)

if result["success"]:
    print(f"Account activated: {result['tx_hash']}")
```

#### Network Configuration

```python
# Access network configurations
networks = oracle.networks
base_config = networks["base"]
starknet_config = networks["starknet"]

print(f"Base RPC: {base_config.rpc_url}")
print(f"StarkNet Chain ID: {starknet_config.chain_id}")
```

### 3. Influence Strategy API

**Purpose**: Automate in-game economic activities and crew management.

#### Initialization

```python
from src.engines.influence import RefiningStrategy, BaseStrategy

# Create strategy instance
strategy = RefiningStrategy(
    dry_run: bool = True,           # Enable/disable dry run mode
    log_fn: Optional[Callable] = None  # Custom logging function
)
```

#### Core Methods

##### `tick() -> None`
**Description**: Execute one strategy cycle
**Usage**:
```python
# Execute single strategy cycle
strategy.tick()

# Run continuous loop
while True:
    strategy.tick()
    await asyncio.sleep(60)  # Wait 1 minute between cycles
```

##### `execute_refine(profit: float) -> None`
**Description**: Execute refining operation
**Parameters**:
- `profit`: Calculated profit margin
**Usage**:
```python
# Called internally by tick(), but can be called manually
strategy.execute_refine(150.0)  # Execute if profit > 100 SWAY
```

#### Crew Management

```python
# Get crew metadata (internal API)
is_busy, busy_until, food_kg, location, class_id = strategy.influence.get_crew_metadata(crew_id)

# Crew status interpretation
class_names = {1: "Engineer", 2: "Miner", 3: "Merchant", 4: "Scientist", 5: "Pilot"}
crew_class = class_names.get(class_id, "Unknown")

print(f"Crew Status: {'Busy' if is_busy else 'Available'}")
print(f"Food Supply: {food_kg}kg")
print(f"Location: {location}")
print(f"Class: {crew_class}")
```

#### Market Analysis

```python
# Market price configuration
market_prices = {
    "Iron Ore": 5.0,
    "Fuel": 2.0,
    "Steel": 20.0,
    "Electronics": 50.0,
    "Ship Hull": 100.0
}

# Calculate profitability
profit = strategy.graph.calculate_profitability("Refine Steel", market_prices)

# Decision making
if profit > 100.0:
    strategy.execute_refine(profit)
else:
    strategy.log("Profit too low - waiting")
```

### 4. Bridge System API

**Purpose**: Handle cross-chain asset transfers and bridge operations.

#### Initialization

```python
from src.engines.bridge_system import BridgeSystem
from src.foundation.network import NetworkOracle
from src.foundation.security import SecurityManager

# Create system instances
oracle = NetworkOracle()
security = SecurityManager()
bridge = BridgeSystem(oracle, security)

await oracle.initialize()
await security.initialize()
```

#### Core Methods

##### `calculate_optimal_bridge_amount(address: str) -> Dict[str, Any]`
**Description**: Calculate optimal bridge amount with gas reserves
**Parameters**:
- `address`: Phantom wallet address
**Returns**: Bridge calculation result
**Usage**:
```python
calc = await bridge.calculate_optimal_bridge_amount("0x1234...")

if calc["success"]:
    print(f"Available: {calc['current_balance']:.6f} ETH")
    print(f"Bridge Amount: {calc['bridge_amount']:.6f} ETH")
    print(f"Gas Reserve: {calc['gas_reserve']:.6f} ETH")
```

##### `execute_bridge_transaction(from_addr: str, to_addr: str, amount: float) -> Dict[str, Any]`
**Description**: Execute bridge transaction with safety checks
**Parameters**:
- `from_addr`: Source Phantom address
- `to_addr`: Target StarkNet address
- `amount`: Amount to bridge
**Returns**: Transaction execution result
**Usage**:
```python
result = await bridge.execute_bridge_transaction(
    "0x1234...", "0x5678...", 0.05
)

if result["success"]:
    print(f"Bridge TX: {result['tx_hash']}")
    print(f"Gas Used: {result['gas_used']}")
else:
    print(f"Error: {result['error']}")
```

#### Bridge Monitoring

```python
# Monitor bridge confirmation status
for tx in bridge.pending_transactions:
    status = await bridge.check_bridge_status(tx.tx_hash)
    print(f"TX {tx.tx_hash}: {status}")

# Print bridge summary
bridge.print_bridge_summary(result)
```

### 5. Security Manager API

**Purpose**: Handle encrypted private key storage and security operations.

#### Initialization

```python
from src.foundation.security import SecurityManager

security = SecurityManager()
await security.initialize()
```

#### Core Methods

##### `unlock_vault(password: str) -> bool`
**Description**: Unlock encrypted security vault
**Parameters**:
- `password`: Vault encryption password
**Returns**: Unlock success status
**Usage**:
```python
success = await security.unlock_vault("secure_password")
if success:
    print("Vault unlocked - private keys accessible")
else:
    print("Invalid password or vault corrupted")
```

##### `get_private_key(key_type: str) -> Optional[str]`
**Description**: Retrieve decrypted private key
**Parameters**:
- `key_type`: Key identifier ("phantom", "starknet", etc.)
**Returns**: Decrypted private key or None
**Usage**:
```python
phantom_key = security.get_private_key("phantom")
if phantom_key:
    print("Phantom private key retrieved")
else:
    print("Key not found or vault locked")
```

##### `store_private_key(key_type: str, private_key: str, password: str) -> bool`
**Description**: Encrypt and store private key
**Parameters**:
- `key_type`: Key identifier
- `private_key`: Private key to store
- `password`: Encryption password
**Returns**: Storage success status
**Usage**:
```python
success = security.store_private_key(
    "phantom", "0xabcdef...", "secure_password"
)
if success:
    print("Private key stored securely")
```

#### Security Status

```python
# Print security status
security.print_security_status()

# Check vault status
is_unlocked = security.is_vault_unlocked()
print(f"Vault Status: {'Unlocked' if is_unlocked else 'Locked'}")
```

### 6. State Registry API

**Purpose**: Persistent state management and transaction tracking.

#### Initialization

```python
from src.foundation.state import StateRegistry

registry = StateRegistry()
await registry.initialize()
```

#### Core Methods

##### `initialize_state(phantom_addr: str, starknet_addr: str) -> RecoveryState`
**Description**: Initialize new recovery state
**Parameters**:
- `phantom_addr`: Phantom wallet address
- `starknet_addr`: StarkNet address
**Returns**: New recovery state object
**Usage**:
```python
state = await registry.initialize_state("0x1234...", "0x5678...")
print(f"State initialized: {state.mission_id}")
```

##### `load_state() -> Optional[RecoveryState]`
**Description**: Load existing recovery state
**Returns**: Recovery state or None if not found
**Usage**:
```python
state = await registry.load_state()
if state:
    print(f"Loaded state: {state.current_phase}")
else:
    print("No existing state found")
```

##### `add_bridge_transaction(tx_hash: str, amount: float, from_addr: str, to_addr: str) -> None`
**Description**: Add bridge transaction to state
**Parameters**:
- `tx_hash`: Transaction hash
- `amount`: Bridge amount
- `from_addr`: Source address
- `to_addr`: Target address
**Usage**:
```python
await registry.add_bridge_transaction(
    "0xabc123...", 0.05, "0x1234...", "0x5678..."
)
```

##### `update_balances(phantom_balance: float, starknet_balance: float) -> None`
**Description**: Update wallet balances
**Parameters**:
- `phantom_balance`: Phantom wallet balance
- `starknet_balance`: StarkNet balance
**Usage**:
```python
await registry.update_balances(0.1234, 0.0567)
```

#### State Queries

```python
# Get current state
state = registry.recovery_state
if state:
    print(f"Current Phase: {state.current_phase}")
    print(f"Security Unlocked: {state.security_unlocked}")
    print(f"Bridge Transactions: {len(state.bridge_transactions)}")
    
    # Get bridge transactions
    for tx in state.bridge_transactions:
        print(f"  {tx.tx_hash}: {tx.status} - {tx.amount} ETH")
```

### 7. Monitoring System API

**Purpose**: Real-time monitoring and alerting for system operations.

#### Initialization

```python
from src.engines.enhanced_monitoring import EnhancedMonitoringSystem

monitoring = EnhancedMonitoringSystem(network_oracle, state_registry)
monitoring.initialize_ui()
```

#### Core Methods

##### `start_stargate_watch(starknet_address: str) -> Dict[str, Any]`
**Description**: Start StarkGate bridge monitoring
**Parameters**:
- `starknet_address`: Address to monitor
**Returns**: Monitoring session result
**Usage**:
```python
result = await monitoring.start_stargate_watch("0x5678...")
if result["success"]:
    print("StarkGate monitoring started")
```

##### `start_ghost_sentry(ghost_address: str, main_wallet: str) -> Dict[str, Any]`
**Description**: Start ghost wallet monitoring
**Parameters**:
- `ghost_address`: Ghost wallet address
- `main_wallet`: Main wallet address
**Returns**: Sentry session result
**Usage**:
```python
result = await monitoring.start_ghost_sentry(
    "0xghost...", "0xmain..."
)
```

##### `stop_monitoring() -> None`
**Description**: Stop all active monitoring
**Usage**:
```python
monitoring.stop_monitoring()
print("All monitoring stopped")
```

#### Alert Configuration

```python
# Configure Telegram alerts (if enabled)
if monitoring.reporting_system.is_enabled():
    await monitoring.reporting_system.bridge_minted(
        amount=0.1, 
        address="0x5678..."
    )
```

## Error Handling

### Common Error Patterns

#### 1. Network Connection Errors
```python
try:
    balance = await oracle.get_balance(address, "starknet")
except ConnectionError as e:
    print(f"Network connection failed: {e}")
    # Retry with different RPC
    await oracle.switch_rpc_provider()
```

#### 2. Security Vault Errors
```python
try:
    key = security.get_private_key("phantom")
except SecurityError as e:
    print(f"Security error: {e}")
    # Handle vault locked/corrupted
```

#### 3. Transaction Failures
```python
result = await bridge.execute_bridge_transaction(from_addr, to_addr, amount)
if not result["success"]:
    error = result.get("error", "Unknown error")
    
    if "insufficient funds" in error.lower():
        print("Insufficient balance for bridge")
    elif "gas price" in error.lower():
        print("Gas price too high")
    else:
        print(f"Bridge failed: {error}")
```

### Error Recovery Strategies

#### Automatic Retry Logic
```python
import asyncio
from typing import Callable

async def retry_with_backoff(
    operation: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0
):
    """Retry operation with exponential backoff"""
    for attempt in range(max_attempts):
        try:
            return await operation()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            
            delay = base_delay * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed, retrying in {delay}s...")
            await asyncio.sleep(delay)
```

#### Graceful Degradation
```python
# Fallback RPC providers
RPC_FALLBACKS = [
    "https://starknet-mainnet.public.blastapi.io",
    "https://1rpc.io/starknet",
    "https://starknet.api.onfinality.io/public"
]

async def get_healthy_rpc():
    """Find healthy RPC provider"""
    for rpc_url in RPC_FALLBACKS:
        try:
            client = FullNodeClient(rpc_url)
            await client.get_block_number()
            return client
        except Exception:
            continue
    
    raise RuntimeError("No healthy RPC available")
```

## Configuration Management

### Environment Variables

```python
import os
from src.foundation.legacy_env import load_env_manual

# Load environment variables
load_env_manual()

# Access configuration
STARKNET_RPC_URL = os.getenv("STARKNET_RPC_URL")
BASE_RPC_URL = os.getenv("BASE_RPC_URL")
PHANTOM_PRIVATE_KEY = os.getenv("PHANTOM_PRIVATE_KEY")
SECURITY_PASSWORD = os.getenv("SECURITY_PASSWORD")
```

### Configuration Validation

```python
def validate_configuration():
    """Validate required environment variables"""
    required_vars = [
        "STARKNET_RPC_URL",
        "BASE_RPC_URL", 
        "PHANTOM_PRIVATE_KEY",
        "SECURITY_PASSWORD"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")
    
    print("Configuration validated successfully")
```

## Performance Optimization

### Connection Pooling
```python
# Reuse network connections across operations
oracle = NetworkOracle()
await oracle.initialize()

# Single instance for multiple operations
balance1 = await oracle.get_balance(addr1, "starknet")
balance2 = await oracle.get_balance(addr2, "starknet")
bridge_result = await oracle.execute_bridge(addr1, addr2, amount)
```

### Batch Operations
```python
# Batch balance checks
addresses = ["0x1234...", "0x5678...", "0x9abc..."]
balances = {}

for addr in addresses:
    balances[addr] = await oracle.get_balance(addr, "starknet")

# Process balances in batch
for addr, balance in balances.items():
    if balance > 0.01:
        print(f"Address {addr} has sufficient balance: {balance}")
```

### Caching Strategy
```python
from functools import lru_cache
from typing import Dict, Any

class CachedNetworkOracle(NetworkOracle):
    """Network oracle with caching"""
    
    @lru_cache(maxsize=128)
    async def get_balance_cached(self, address: str, network: str) -> float:
        """Cached balance check"""
        return await super().get_balance(address, network)
    
    def clear_cache(self):
        """Clear balance cache"""
        self.get_balance_cached.cache_clear()
```

## Testing and Development

### Mock Services
```python
from unittest.mock import AsyncMock, MagicMock

# Mock network oracle for testing
mock_oracle = AsyncMock()
mock_oracle.get_balance.return_value = 1.0
mock_oracle.execute_bridge.return_value = {
    "success": True,
    "tx_hash": "0xmock123...",
    "amount": 0.1
}

# Test with mock
kernel = RecoveryKernel("0x1234...", "0x5678...")
kernel.network_oracle = mock_oracle
```

### Dry Run Mode
```python
# Enable dry run for safe testing
strategy = RefiningStrategy(dry_run=True)
kernel = RecoveryKernel("0x1234...", "0x5678...")

# All operations will be simulated
await kernel.execute_recovery()  # No actual transactions
strategy.tick()  # No actual refining
```

### Integration Testing
```python
async def test_full_workflow():
    """Test complete recovery workflow"""
    # Setup test environment
    kernel = RecoveryKernel(test_phantom_addr, test_starknet_addr)
    
    # Initialize with test network
    await kernel.initialize()
    
    # Test each phase
    assert await kernel.unlock_security("test_password")
    assert await kernel.check_gas_safety()
    
    # Verify state transitions
    assert kernel.current_phase == RecoveryPhase.BRIDGE_EXECUTING
    
    print("Integration test passed")
```

## Best Practices

### 1. Resource Management
```python
# Proper cleanup
async def cleanup():
    if kernel:
        await kernel.shutdown()
    if oracle:
        await oracle.shutdown()
    if security:
        await security.shutdown()

# Use context managers when possible
async with RecoveryKernel(addr1, addr2) as kernel:
    await kernel.execute_full_auto()
```

### 2. Logging and Monitoring
```python
import logging
from loguru import logger

# Configure structured logging
logger.add(
    "logs/api_usage.log",
    rotation="1 day",
    retention="30 days",
    level="INFO"
)

# Log API calls
logger.info("Bridge operation started", extra={
    "from_address": from_addr,
    "to_address": to_addr,
    "amount": amount
})
```

### 3. Security Practices
```python
# Never log private keys
logger.info("Private key retrieved")  # ✅ Good
# logger.info(f"Private key: {private_key}")  # ❌ Bad

# Use secure key handling
def secure_key_operation(key: str):
    """Perform operation without logging key"""
    try:
        # Operation logic here
        result = process_key(key)
        logger.info("Key operation successful")
        return result
    except Exception as e:
        logger.error("Key operation failed")
        raise
    finally:
        # Clear key from memory if sensitive
        del key
```

### 4. Error Handling
```python
# Comprehensive error handling
async def safe_bridge_execution(from_addr: str, to_addr: str, amount: float):
    """Execute bridge with comprehensive error handling"""
    try:
        # Pre-flight checks
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if not await kernel.check_gas_safety():
            raise RuntimeError("Gas prices too high")
        
        # Execute bridge
        result = await oracle.execute_bridge(from_addr, to_addr, amount)
        
        if not result["success"]:
            raise RuntimeError(f"Bridge failed: {result['error']}")
        
        return result
        
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise
    except RuntimeError as e:
        logger.error(f"Bridge execution failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

## Troubleshooting API Issues

### Common Problems

#### 1. Initialization Failures
```python
# Check network connectivity
async def diagnose_network():
    try:
        await oracle.initialize()
        print("Network oracle initialized successfully")
    except Exception as e:
        print(f"Network initialization failed: {e}")
        
        # Check RPC endpoints
        for name, config in oracle.networks.items():
            print(f"{name} RPC: {config.rpc_url}")
```

#### 2. Security Vault Issues
```python
# Diagnose vault problems
def diagnose_vault():
    if not security.is_vault_unlocked():
        print("Vault is locked")
        return
    
    try:
        keys = security.list_stored_keys()
        print(f"Stored keys: {keys}")
    except Exception as e:
        print(f"Vault access error: {e}")
```

#### 3. State Persistence Issues
```python
# Check state file
async def diagnose_state():
    try:
        state = await registry.load_state()
        if state:
            print(f"State loaded: {state.current_phase}")
        else:
            print("No state file found")
    except Exception as e:
        print(f"State loading error: {e}")
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable verbose API responses
kernel.debug_mode = True
oracle.verbose = True
```

## API Reference Summary

| Module | Primary Purpose | Key Methods |
|--------|------------------|-------------|
| RecoveryKernel | Account recovery automation | execute_full_auto(), execute_recovery() |
| NetworkOracle | Blockchain network operations | get_balance(), execute_bridge() |
| InfluenceStrategy | Game automation | tick(), execute_refine() |
| BridgeSystem | Cross-chain transfers | calculate_optimal_bridge_amount() |
| SecurityManager | Key encryption/decryption | unlock_vault(), get_private_key() |
| StateRegistry | Persistent state management | load_state(), update_balances() |
| MonitoringSystem | Real-time monitoring | start_stargate_watch(), stop_monitoring() |

This API guide provides comprehensive coverage of all available functionality. For specific implementation details, refer to the source code in each module.
