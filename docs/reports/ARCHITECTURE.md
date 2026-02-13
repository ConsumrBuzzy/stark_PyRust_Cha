# Architecture Documentation

## 🏗️ System Architecture Overview

Stark_PyRust_Chain is a multi-paradigm system designed for Starknet account orchestration, fund recovery, and gas-efficient bridge management. The architecture demonstrates boundary-first design principles with clear separation between Python orchestration and high-performance systems logic.

## 📐 Architectural Patterns

### 1. Boundary-First Design

The system is organized around clear boundaries between different concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL INTERFACES                     │
├─────────────────────────────────────────────────────────────────┤
│  Coinbase CDP  │  StarkNet RPC  │  Orbiter Bridge  │  Web3 Base    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ADAPTER LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  starknet-py  │  web3.py       │  Custom APIs    │  Rate Limiting │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                      │
├─────────────────────────────────────────────────────────────────┤
│  Ghost Sweep   │  Inflow Chaser │  Account Discovery │  Sentry Loop │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                     │
├─────────────────────────────────────────────────────────────────┤
│  Config Mgmt  │  Error Handling │  Logging System  │  Monitoring   │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Multi-Provider Resilience

The system implements a round-robin RPC provider pattern to ensure high availability:

```python
class RPCManager:
    def __init__(self):
        self.urls = [
            os.getenv("STARKNET_MAINNET_URL"),
            os.getenv("STARKNET_LAVA_URL"),
            os.getenv("STARKNET_1RPC_URL"),
            os.getenv("STARKNET_ONFINALITY_URL")
        ]
        self.urls = [u for u in self.urls if u]
        self.current_idx = 0

    async def call_with_rotation(self, func, *args, **kwargs):
        for _ in range(len(self.urls) or 1):
            url = self.get_next_url()
            client = FullNodeClient(node_url=url)
            try:
                return await func(client, *args, **kwargs)
            except Exception as e:
                # Handle rate limits, version incompatibility, etc.
                continue
```

### 3. Environment-Driven Configuration

All sensitive data is externalized to environment variables:

```python
# ✅ Secure - Environment-based
private_key = os.getenv("STARKNET_PRIVATE_KEY")
rpc_url = os.getenv("STARKNET_MAINNET_URL")
target_address = os.getenv("STARKNET_WALLET_ADDRESS")

# ❌ Insecure - Hardcoded
private_key = "0x1234567890abcdef..."
rpc_url = "https://starknet-mainnet.g.alchemy.com/..."
```

## 🔧 Core Components

### Ghost Sweep Protocol

The Ghost Sweep Protocol handles automated recovery of funds from EVM-derived Starknet addresses:

```python
class GhostSweep:
    def __init__(self):
        self.ghost_address = self.get_ghost_address()
        self.rpc_manager = RPCManager()
        
    async def monitor_and_sweep(self):
        balance = await self.check_balance()
        if balance > self.threshold:
            return await self.execute_sweep()
```

**Key Features**:
- Deterministic address derivation from EVM keys
- Multi-RPC resilience for balance checking
- Automated sweep execution when funds detected
- Configurable thresholds and targets

### Inflow Chaser System

The Inflow Chaser provides CDP-integrated capital injection:

```python
class InflowChaser:
    def __init__(self):
        self.cdp_client = self.setup_cdp()
        self.transit_address = os.getenv("TRANSIT_EVM_ADDRESS")
        
    async def send_chaser_usdc(self, amount=15.00):
        wallet = self.get_or_create_wallet()
        transfer = wallet.transfer(
            amount, "usdc", self.transit_address, gasless=True
        ).wait()
```

**Key Features**:
- Coinbase CDP SDK integration
- Gasless transfers on Base network
- Wallet reuse to avoid rate limits
- Automatic fallback to manual creation

### Account Discovery Engine

The Account Discovery system attempts to reverse-engineer proprietary wallet implementations:

```python
class AccountDiscovery:
    def __init__(self):
        self.known_hashes = self.load_argent_class_hashes()
        self.salt_range = range(0, 1000)
        
    async def find_parameters(self, target_address):
        for class_hash in self.known_hashes:
            for salt in self.salt_range:
                for pattern in self.constructor_patterns:
                    if self.compute_address(class_hash, pattern, salt) == target_address:
                        return {"class_hash": class_hash, "salt": salt, "pattern": pattern}
```

## 🚨 Case Study: The Ready.co Paradox

### Problem Statement

The Ready.co platform created a proprietary wallet implementation that resulted in a **Vendor Lock-in** scenario:

```
User Action: Create wallet via Ready.co web interface
├─────────────────────────────────────────────────────────────────┐
│                    READY.CO BLACK BOX                         │
│  • Custom class hash (not public)                              │
│  • Non-standard salt derivation                                 │
│  • Proprietary constructor pattern                              │
│  • No CLI deployment method                                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
Result: Counterfactual account with funds but no deployment path
```

### Technical Impact

**What Went Wrong**:
- Standard Argent class hashes: ❌ No match
- Common salt values (0, 1): ❌ No match  
- Constructor patterns: ❌ No match
- 10,000+ combinations tested: ❌ No match

**Root Cause Analysis**:
1. **Proprietary SDK**: Ready.co used custom implementation
2. **No Documentation**: Class hash not publicly available
3. **No CLI Access**: Web-only wallet creation
4. **Vendor Lock-in**: Funds trapped without official interface

### Lessons Learned

**For Developers**:
- Avoid proprietary SDKs for critical operations
- Always test with small amounts first
- Ensure CLI deployment paths exist
- Document all derivation parameters

**For Architects**:
- Design for portability from day one
- Provide multiple recovery paths
- Implement fallback mechanisms
- Consider open-source alternatives

## 🔒 Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYERED SECURITY                           │
├─────────────────────────────────────────────────────────────────┤
│  Application:    │  Network:        │  Data:           │
│  • Input Validation │  • RPC Encryption│  • Env Variables │
│  • Simulation     │  • Rate Limiting  │  • AES-256 at Rest │
│  • Error Handling  │  • Failover      │  • No Hardcoded   │
└─────────────────────────────────────────────────────────────────┘
```

### Threat Model

| Asset | Threat Vector | Mitigation |
|-------|----------------|------------|
| Private Keys | Environment leakage | Environment variables + .gitignore |
| API Keys | Repository exposure | No hardcoded keys + encryption |
| RPC Calls | Malicious providers | Multi-provider resilience |
| Transactions | Replay attacks | Nonce management + simulation |

## 📊 Performance Characteristics

### Metrics

| Operation | Average Latency | Success Rate | Gas Efficiency |
|-----------|----------------|-------------|----------------|
| Balance Check | <2s | 95%+ | Optimized |
| Transaction | <5s | 90%+ | v0.14.0+ compatible |
| Discovery | <10s | 0% (proprietary) | N/A |

### Bottlenecks

**Current Limitations**:
- RPC provider rate limits
- Starknet network congestion
- Proprietary wallet incompatibility

**Optimization Opportunities**:
- Rust core for cryptographic operations
- Connection pooling for RPC calls
- Parallel balance checking

## 🔄 Migration Path: The Strangler Pattern

### Phase 1: Analysis (Week 1)
- Identify performance bottlenecks
- Profile Python operations
- Define Rust module boundaries

### Phase 2: Rust Prototyping (Week 2-3)
```rust
// Rust core for cryptographic operations
pub struct AccountDiscovery {
    pub fn compute_address(&self, class_hash: u64, salt: u64) -> u64 {
        // High-performance address computation
    }
}
```

### Phase 3: Integration (Week 4)
```python
# Python wrapper for Rust core
from rust_core import AccountDiscovery

discovery = AccountDiscovery()
result = discovery.find_parameters(target_address)
```

### Phase 4: Optimization (Week 5-6)
- Zero-copy data transfer
- Parallel processing
- Performance benchmarking

## 📋 Design Decisions (ADRs)

### ADR-047: Transit Wallet Architecture
**Decision**: Use intermediate transit wallets for cross-chain operations
**Rationale**: Minimizes exposure and maximizes recovery options
**Impact**: Additional complexity but improved security

### ADR-049: Ghost Address Derivation
**Decision**: Standardized EVM-to-Starknet address mapping
**Rationale**: Enables cross-chain fund tracking
**Impact**: Simplified monitoring and recovery

### ADR-080: Emergency Exit Protocol
**Decision**: Multiple recovery paths with manual fallbacks
**Rationale**: Handles edge cases and vendor lock-in scenarios
**Impact**: Increased resilience but higher complexity

## 🔮 Future Architecture

### Target State (Rust-Enhanced)

```
┌─────────────────────────────────────────────────────────────────┐
│                    PYTHON LAYER (Orchestration)                │
├─────────────────────────────────────────────────────────────────┤
│  • Strategy Logic  │  • User Interface  │  • Workflow Mgmt │
│  • API Coordination│  • Error Handling  │  • Logging      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ PyO3 Interface
┌─────────────────────────────────────────────────────────────────┐
│                    RUST CORE (Performance)                        │
├─────────────────────────────────────────────────────────────────┤
│  • Crypto Ops     │  • Parallel Proc   │  • Memory Safety  │
│  • Data Processing│  • Zero-Copy     │  • Type Safety   │
│  • Computation    │  • Performance   │  • Reliability  │
└─────────────────────────────────────────────────────────────────┘
```

### Integration Strategy

**Boundary Definition**:
- **Python**: Orchestration, UI, I/O operations
- **Rust**: Cryptography, computation, data processing
- **Interface**: PyO3 with type-safe data transfer

**Migration Benefits**:
- 10-100x performance for cryptographic operations
- Memory safety for critical operations
- Parallel processing for batch operations

---

## 📚 References

- [Starknet Documentation](https://docs.starknet.io/)
- [PyO3 Guide](https://pyo3.rs/)
- [Rust Book](https://doc.rust-lang.org/book/)
- [Multi-Paradigm Systems Design Patterns](https://patterns.dev/)

---

*Architecture maintained by PyPro-Systems: Boundary-First Design for Multi-Paradigm Solutions*
