# StarkNet Infrastructure - Hardened

A professional StarkNet infrastructure suite with L7 DPI bypass capabilities and automated account management.

## Architecture

```
stark_PyRust_Chain/
├── core/               # Core infrastructure modules
│   ├── providers.py    # RPC resilience and rotation
│   ├── shadow.py       # L7 DPI bypass (ERC-20 calls)
│   └── models.py       # Pydantic data models
├── tools/              # Operational scripts
│   ├── sentry.py       # Ghost monitoring (Shadow Protocol)
│   ├── activate.py     # Account activation
│   └── inventory.py    # Balance auditing
├── docs/               # Documentation
│   ├── ARCHITECTURE.md # System architecture
│   └── SECURITY.md     # Security analysis
└── data/               # Persistent data (gitignored)
    └── reports/        # Generated reports
```

## Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
# STARKNET_WALLET_ADDRESS, STARKNET_PRIVATE_KEY, etc.
```

### 2. Virtual Environment

```bash
# Setup Python 3.12 environment
python setup_venv.py

# Activate manually
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate   # Windows
```

### 3. Core Operations

#### Monitor Ghost Funds (L7 DPI Bypass)
```bash
python tools/sentry.py
```

#### Activate Undeployed Account
```bash
python tools/activate.py
```

#### Audit Balances
```bash
python tools/inventory.py
```

#### Diagnose RPC Health
```bash
python core/providers.py
```

## Security Features

### L7 DPI Bypass
- Uses ERC-20 contract calls instead of account state queries
- Bypasses Deep Packet Inspection filtering
- Works without VPN in restrictive network environments

### RPC Resilience
- Multi-provider rotation with health monitoring
- Automatic failover and recovery
- Provider performance analytics

## Capabilities

- **Balance Monitoring**: Real-time ETH balance tracking
- **Account Activation**: Self-funded proxy deployment
- **Transaction Recovery**: Ghost fund sweep automation
- **Network Diagnostics**: Comprehensive RPC analysis
- **Shadow Protocol**: Stealth monitoring capabilities

## Development

### Core Modules
- `core/providers.py`: NetworkSentinel class for RPC management
- `core/shadow.py`: ShadowStateChecker for L7 bypass
- `core/models.py`: Pydantic data contracts

### Tools
- `tools/sentry.py`: Production Ghost monitoring
- `tools/activate.py`: Account deployment automation
- `tools/inventory.py`: Multi-chain balance auditing

## Architecture

This system demonstrates advanced blockchain infrastructure techniques:

1. **L7 DPI Bypass**: Circumvents network-level filtering
2. **RPC Resilience**: Handles provider failures gracefully
3. **Shadow Protocol**: Stealth balance monitoring
4. **Automated Recovery**: Ghost fund detection and sweep

## Requirements

- Python 3.12+
- starknet-py
- aiohttp
- loguru
- rich
- pydantic

See `requirements.txt` for complete dependency list.

## Monitoring

The system includes comprehensive logging and reporting:
- Real-time console output
- Structured log files
- Markdown audit reports
- Telegram notifications (optional)

## Security Notes

- Never commit `.env` files
- Use secure RPC endpoints
- Monitor for unauthorized access
- Keep private keys secure

---
*Hardened StarkNet Infrastructure with L7 DPI Bypass*
