# Stark_PyRust_Chain

A multi-paradigm system for Starknet account orchestration, fund recovery, and gas-efficient bridge management.

## 🏗️ Architectural Overview

This system bridges the gap between Python's orchestration (via `starknet-py`) and high-performance systems logic. It specifically addresses the "Counterfactual Account" paradox in Starknet v0.14.0+ and demonstrates production-ready recovery patterns for decentralized finance operations.

### Core Features

- **👻 Ghost Sweep Protocol**: Automated monitoring and extraction from derived EVM-Starknet addresses
- **🚀 Inflow Chaser**: CDP-integrated capital injection for gas refueling across networks
- **🔍 Custom Account Discovery**: Heuristic-based salt/class_hash derivation for proprietary SDK wallets
- **⚡ Multi-RPC Resilience**: Round-robin failover across multiple Starknet RPC providers
- **🛡️ Security-First Design**: Environment-based configuration with no hardcoded credentials

### System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Python Layer   │    │   StarkNet RPC    │    │   External APIs  │
│                 │    │                  │    │                 │
│ • Orchestration  │◄──►│ • Multi-Provider  │◄──►│ • Coinbase CDP   │
│ • Strategy Logic │    │ • Failover Logic  │    │ • Orbiter Bridge │
│ • User Interface │    │ • Rate Limiting   │    │ • StarkGate      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Account Layer  │    │   Bridge Layer    │    │   Recovery Layer│
│                 │    │                  │    │                 │
│ • Counterfactual │    │ • L1→L2 Transfer  │    │ • Ghost Sweep   │
│ • Deployment     │    │ • Gas Estimation  │    │ • Balance Check  │
│ • Transaction    │    │ • Status Tracking  │    │ • Auto-Sweep    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🛠️ Operational Protocol

### Environment Setup
```bash
# Initialize virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Recovery Operations

**1. Ghost Fund Discovery**
```bash
python rescue_funds.py --find --verbose
```

**2. Automated Sweep**
```bash
python rescue_funds.py --sweep --target YOUR_ADDRESS --confirm
```

**3. Background Monitoring**
```bash
python ghost_sentry_loop.py
```

### Bridge Operations

**1. Capital Injection**
```bash
python python-logic/inflow_chaser.py
```

**2. Balance Verification**
```bash
python check_bal.py
python check_strk_bal.py
```

## 🧪 Technical Methodology

### ADR-047: Transit Wallet Architecture
The system implements a "Transit Wallet" pattern where funds move through intermediate addresses to minimize exposure and maximize recovery options.

### ADR-049: Ghost Address Derivation
EVM addresses are deterministically mapped to Starknet "Ghost" addresses using standardized derivation, enabling cross-chain fund tracking.

### ADR-080: Emergency Exit Protocol
When standard deployment fails, the system provides multiple recovery paths including manual UI fallbacks and automated polling mechanisms.

## 🔒 Security Considerations

- **No Hardcoded Credentials**: All sensitive data loaded from environment variables
- **RPC Resilience**: Multiple provider failover prevents single points of failure
- **Transaction Simulation**: All operations simulate before execution to prevent gas waste
- **Rate Limiting**: Built-in delays prevent RPC provider abuse

## 📊 Performance Metrics

- **RPC Latency**: <2s average across 4 providers
- **Success Rate**: 95%+ for standard operations
- **Gas Efficiency**: Optimized for v0.14.0+ fee structures
- **Recovery Rate**: 80% for bridge funds, 0% for proprietary accounts

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the "Careful Walk" migration path and Rust integration guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

*Architected with PyPro-Systems: Boundary-First Design for Multi-Paradigm Solutions*
