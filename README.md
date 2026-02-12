# stark_PyRust_Chain: The Decade Device

**Automated Starknet/Influence Strategy Engine**
*Rust-Powered. Python-Capped. Pulse-Driven.*

## Overview
`stark_PyRust_Chain` is a hybrid high-performance bot designed to automate complex supply chain logistics within the Influence ecosystem on Starknet. It leverages Rust for heavy computation (cryptography, graph traversal) and Python for strategic orchestration.

**Objective**: Create a "Decade Device" - a setup-and-forget generator that operates with 99.9% reliability using GitHub Actions "Pulse" architecture.

## Architecture
-   **Rust Core (`rust-core/`)**:
    -   `Vault`: AES-256 Credential Management.
    -   `StarknetClient`: Round-Robin RPC, Gas/Nonce/Balance Tracking.
    -   `InfluenceAPI`: Market Data & Crew Status (Food, Busy State, Class).
    -   `SupplyChain`: DAG-based Profit Optimization.
-   **Python Logic (`python-logic/`)**:
    -   `Orchestrator`: Main Command Center.
    -   `StrategyModule`: "Refining Spread" Logic + Guardrails.
    -   `Dashboard`: "The Decade Device" TUI.
    -   `Onramp`: Coinbase -> Starknet Bridge.

## Validated Guardrails (ADRs)
| ADR | Feature | Guardrail Implemented |
| :--- | :--- | :--- |
| **029** | **Mainnet Launch** | Max Gas < 30 Gwei. ETH Balance Check. |
| **031** | **Ghost Scanner** | ROI > 150 SWAY/Batch (Verified via SAGE). |
| **035** | **Cross-Chain** | Onramp Bridge with Regex Validation. |
| **038** | **Pulse Automation** | GitHub Actions (30m Interval) + Secret Masking. |
| **040** | **Logistics** | Nonce Persistence & Logistics Penalty (-15 SWAY/Lot). |
| **041** | **Life Support** | Busy Check (Gas Save). Food Check (Efficiency). |
| **043** | **Mechanics** | Engineer Class Affinity. Propellant Locking. |

## Quick Start

### 1. Requirements
-   Python 3.10+
-   Rust (Cargo)
-   Starknet Wallet (Argent/Braavos)

### 2. Installation
```powershell
# Clone & Setup
git clone https://github.com/YourRepo/stark_PyRust_Chain.git
cd stark_PyRust_Chain

# Build the Rust Extension
python build_rust.py
```

### 3. Usage
**Interactive Mode (TUI):**
```powershell
python python-logic/orchestrator.py start
```
**Pulse Mode (Single Shot):**
```powershell
python python-logic/orchestrator.py pulse
```
**Verification Scripts:**
-   `verify_status.py`: Check Crew Health/Class.
-   `verify_logistics.py`: Check Nonce/Location.
-   `onramp.py`: Bridge Funds.

## Deployment
1.  **Fund Wallet**: ~$12.00 ETH.
2.  **Recruit**: 1x Engineer.
3.  **GitHub Secrets**:
    -   `STARKNET_RPC_URL`
    -   `STARKNET_PRIVATE_KEY`
    -   `STARKNET_WALLET_ADDRESS`
4.  **Push**: The `.github/workflows/bot_pulse.yml` will auto-start.

---
*Built with PyPro-Systems.*
