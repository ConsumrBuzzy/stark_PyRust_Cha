# Influence Game - Complete User Guide

## Overview

**Influence** is a fully onchain space strategy MMO built on StarkNet, where players colonize the Adalian asteroid belt in a persistent blockchain world. This project provides automation and infrastructure tools for managing StarkNet accounts and operations within the Influence ecosystem.

### Game Context

- **Setting**: Realistic asteroid belt around the star Adalia
- **Genre**: Space strategy MMO (similar to Eve Online, Stellaris, Elite Dangerous)
- **Blockchain**: StarkNet (Layer 2 on Ethereum)
- **Launch**: June 27, 2024 - Live on Mainnet
- **Developer**: Unstoppable Games, Inc.

## Game Mechanics

### Core Gameplay Elements

#### 1. Crew Management
Players control **Crewmates** organized into crews, with five primary classes:
- **Miner**: Extract raw materials from asteroids
- **Merchant**: Handle trading and market operations
- **Engineer**: Build and maintain infrastructure
- **Scientist**: Research and development
- **Pilot**: Navigate and transport cargo

#### 2. Resource Economy
- **22 raw materials** from **11 asteroid types**
- **200+ craftable goods** (ship hulls, electronics, warehouses)
- **Scientifically-based production chains** modeled on reality
- **Player-driven marketplaces** and supply chains

#### 3. Asteroid Colonization
- **Realistic orbital mechanics** in real-time
- **Settlement construction** and expansion
- **Lot management** and leasing systems
- **Long-range scanning** for resource discovery

#### 4. Strategic Elements
- **Resource gathering** and trade routes
- **Infrastructure development** (refineries, factories, shipyards)
- **Diplomacy** and player collaboration
- **Economic warfare** and espionage opportunities

### Game Stages

1. **Exploitation Phase**: Resource discovery and initial colonization
2. **Discovery Phase**: Advanced exploration and technology
3. **Conflict Phase**: Strategic competition and dominance

## This Project's Role

### Primary Purpose

This **PyRust Chain** project provides **automation infrastructure** for Influence players, focusing on:

#### Account Management
- **Phantom wallet recovery** and fund bridging
- **StarkNet account deployment** and activation
- **Multi-wallet orchestration** for crew management

#### Economic Automation
- **Bridge operations** between Base and StarkNet
- **Gas optimization** and cost management
- **Automated refining** strategies (Iron → Steel)
- **Supply chain optimization**

#### Monitoring & Analytics
- **Real-time balance tracking**
- **Transaction monitoring** and status updates
- **ROI calculation** and profitability analysis
- **Dashboard interfaces** for strategic oversight

### Key Components

#### 1. Recovery Kernel (`src/engines/recovery_kernel.py`)
**Purpose**: Unified state machine for account recovery and deployment
**Features**:
- Phantom wallet fund bridging
- StarkNet account activation
- Transaction monitoring
- Safety checks and gas optimization

#### 2. Influence Strategy Engine (`src/engines/influence.py`)
**Purpose**: Automates in-game economic activities
**Features**:
- Crew status monitoring
- Resource refining automation
- Profitability calculation
- Market opportunity detection

#### 3. Bridge System (`src/engines/bridge_system.py`)
**Purpose**: Handles cross-chain asset transfers
**Features**:
- Base → StarkNet bridging via StarkGate
- Gas reserve optimization
- Transaction confirmation tracking
- Multiple bridge adapter support

#### 4. Network Oracle (`src/foundation/network.py`)
**Purpose**: Unified blockchain network management
**Features**:
- Multi-network support (Base, StarkNet)
- RPC health monitoring
- Balance checking
- Connection management

## Getting Started

### Prerequisites

1. **StarkNet Wallet**: Argent or Braavos wallet
2. **Phantom Wallet**: For Base network operations
3. **ETH Balance**: For gas fees and bridge operations
4. **Environment Setup**: Python 3.12+ with required dependencies

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/stark_PyRust_Chain.git
cd stark_PyRust_Chain

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup Rust components (optional)
pip install maturin
cd rust-core && maturin develop
```

### Configuration

1. **Environment Setup**:
```bash
cp .env.example .env
# Edit .env with your wallet addresses and private keys
```

2. **Required Environment Variables**:
```
# StarkNet Configuration
STARKNET_WALLET_ADDRESS=0x...
STARKNET_RPC_URL=https://...
PHANTOM_PRIVATE_KEY=...

# Base Network
BASE_RPC_URL=https://...

# Bridge Configuration
STARGATE_BRIDGE_ADDRESS=0x...
STARKNET_ETH_CONTRACT=0x...

# Security
SECURITY_PASSWORD=your_encryption_password
```

### Basic Usage

#### 1. Account Recovery
```python
from src.engines.recovery_kernel import RecoveryKernel

# Initialize kernel
kernel = RecoveryKernel(
    phantom_address="0x...",
    starknet_address="0x..."
)

# Execute full auto recovery
success = await kernel.execute_full_auto()
```

#### 2. Influence Strategy
```python
from src.engines.influence import RefiningStrategy

# Initialize strategy
strategy = RefiningStrategy(dry_run=True)

# Run strategy tick
strategy.tick()
```

#### 3. Bridge Operations
```python
from src.engines.bridge_system import BridgeSystem

# Initialize bridge system
bridge = BridgeSystem(network_oracle, security_manager)

# Execute bridge
result = await bridge.execute_bridge_transaction(
    from_address="0x...",
    to_address="0x...",
    amount=0.1
)
```

## Advanced Features

### 1. Multi-Crew Management
The system supports managing multiple crews simultaneously:
- **Crew status monitoring** via Influence API
- **Automated task assignment** based on crew class
- **Resource allocation** optimization
- **Cross-crew coordination** strategies

### 2. Economic Automation
#### Refining Strategy
```python
# Iron → Steel refining automation
strategy = RefiningStrategy(dry_run=False)
strategy.tick()  # Executes one cycle
```

#### Market Monitoring
```python
# Real-time price tracking
prices = await influence.get_market_prices()
profit = strategy.calculate_profitability(prices)
```

### 3. Security & Safety
#### Vault Security
- **Encrypted private key storage**
- **Password-based vault access**
- **Automatic lockout** on failed attempts
- **Audit logging** of all operations

#### Gas Optimization
- **Dynamic gas price monitoring**
- **Safety caps** for full-auto operations
- **Cost-benefit analysis** before transactions
- **Retry logic** with exponential backoff

### 4. Monitoring & Analytics
#### Real-time Dashboard
```python
from src.core.ui.dashboard import RichDashboard

dashboard = RichDashboard()
dashboard.start()  # Launches TUI interface
```

#### Transaction Tracking
- **Bridge confirmation monitoring**
- **Activation status tracking**
- **Balance change notifications**
- **Telegram integration** for alerts

## Operational Modes

### 1. Full-Auto Mode
**Purpose**: Complete automation of recovery and deployment
**Features**:
- Automatic security unlocking
- Gas price safety checks
- Optimized bridge execution
- Account deployment automation

```python
success = await kernel.execute_full_auto()
```

### 2. Manual Mode
**Purpose**: Step-by-step control with confirmation prompts
**Features**:
- Interactive prompts for each step
- Dry-run capabilities
- Manual approval required
- Detailed logging

```python
await kernel.initialize()
await kernel.unlock_security(password="your_password")
await kernel.execute_recovery()
```

### 3. Monitoring Mode
**Purpose**: Passive observation and alerting
**Features**:
- Real-time balance tracking
- Transaction monitoring
- Alert notifications
- Historical analysis

```python
await kernel.start_stargate_watch(starknet_address)
```

## Troubleshooting

### Common Issues

#### 1. Bridge Failures
**Symptoms**: Bridge transactions not confirming
**Solutions**:
- Check gas price settings
- Verify Phantom wallet balance
- Confirm StarkGate contract address
- Check network connectivity

#### 2. Account Activation Issues
**Symptoms**: StarkNet account not deploying
**Solutions**:
- Verify ETH balance on StarkNet
- Check account class hash
- Confirm private key format
- Review gas limit settings

#### 3. Connection Problems
**Symptoms**: RPC connection failures
**Solutions**:
- Test RPC endpoint accessibility
- Check network firewall settings
- Verify API rate limits
- Try alternative RPC URLs

### Debug Mode
Enable detailed logging for troubleshooting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Checks
Run system diagnostics:
```bash
python scripts/system_health_audit.py
```

## Best Practices

### 1. Security
- **Never commit private keys** to version control
- **Use strong encryption passwords**
- **Regularly rotate API keys**
- **Monitor for unauthorized access**

### 2. Gas Optimization
- **Monitor gas prices** before transactions
- **Use safety caps** for automation
- **Batch operations** when possible
- **Consider off-peak hours** for lower fees

### 3. Strategy Planning
- **Start with dry-run mode** to test strategies
- **Monitor profitability** before scaling
- **Diversify crew assignments**
- **Maintain liquidity reserves**

### 4. Monitoring
- **Set up alerts** for important events
- **Review transaction history** regularly
- **Track ROI metrics**
- **Monitor system health**

## Integration with Influence

### API Connections
The system integrates with Influence through:
- **StarkNet smart contracts** for game state
- **Crew status APIs** for real-time monitoring
- **Market data feeds** for price information
- **Event listeners** for game events

### Game-Specific Features

#### Crew Automation
```python
# Monitor crew status
is_busy, busy_until, food_kg, location, class_id = influence.get_crew_metadata(crew_id)

# Automated task assignment
if not is_busy and food_kg > 550:
    strategy.execute_refine(profit_margin)
```

#### Resource Management
```python
# Track resource inventory
inventory = await influence.get_crew_inventory(crew_id)

# Optimize refining decisions
if inventory.get("Iron Ore", 0) > 100:
    strategy.execute_refine("Iron -> Steel")
```

#### Market Operations
```python
# Monitor market prices
market_data = await influence.get_market_prices()

# Calculate arbitrage opportunities
opportunities = strategy.find_arbitrage(market_data)
```

## Community & Support

### Resources
- **Influence Discord**: https://discord.gg/influenceth
- **StarkNet Documentation**: https://docs.starknet.io/
- **Game Wiki**: https://wiki.influenceth.io/
- **Project GitHub**: https://github.com/your-org/stark_PyRust_Chain

### Getting Help
1. **Check the logs** for error details
2. **Review troubleshooting section**
3. **Join community Discord**
4. **Create GitHub issue** with details

## Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Code formatting
black src/
ruff src/
```

### Contribution Guidelines
- **Follow SOLID principles**
- **Add type hints** for all functions
- **Write comprehensive tests**
- **Update documentation**
- **Use semantic commits**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is provided for educational and research purposes. Users are responsible for:
- **Compliance with game terms of service**
- **Security of their private keys**
- **Financial risks of automation**
- **Legal compliance in their jurisdiction**

Always start with **dry-run mode** and small amounts when testing new strategies.
