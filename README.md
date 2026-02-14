# StarkNet Shadow Protocol

> **🚨 CRITICAL**: Project Retired - $63 USD Loss | [Post Mortem Analysis](docs/POST_MORTEM_ANALYSIS.md) | [Situation Report](docs/STARKNET_FUNDS_LOCKED_SITUATION.md)

A comprehensive StarkNet account management and deployment system demonstrating blockchain deployment economics, failure analysis, and professional post-mortem documentation.

## 🚨 **CRITICAL SITUATION**

### [2026-02-13] - 🚨 CRITICAL: Project Retirement
- **CRITICAL**: 0.014863 ETH (~$52 USD) locked in undeployed StarkNet account
- **Total Loss**: $63 USD (including bridge fees and failed attempts)
- **Issue**: Cannot deploy account due to extreme gas prices (~42,000 Gwei)
- **Deployment Cost**: ~24 ETH (not feasible with current balance)
- **Status**: Funds permanently locked, project retired
- **Documentation**: Added comprehensive situation report and post mortem analysis
- **Impact**: Account cannot send transactions or transfer funds
- **Retirement**: Project retired, open to community fork
- **Legacy**: Complete failure analysis for community learning

### **📚 Documentation**
📄 **[Situation Report](docs/STARKNET_FUNDS_LOCKED_SITUATION.md)** - Complete incident analysis
🔍 **[Post Mortem Analysis](docs/POST_MORTEM_ANALYSIS.md)** - Industry-standard failure analysis
📖 **[Architecture](docs/ARCHITECTURE.md)** - System design and components
📋 **[Contributing](CONTRIBUTING.md)** - Development guidelines
🔒 **[Security](SECURITY.md)** - Security practices
🧪 **[Testing](TESTING.md)** - Testing framework
🔍 **[SEO Optimization](docs/SEARCH_ENGINE_OPTIMIZATION.md)** - Search engine optimization guide

---

# stark_PyRust_Chain

Public/portfolio-ready refactor with Python 3.12 + Rust (PyO3) engines. Legacy `python-logic/` scripts are thin wrappers or deprecated stubs; core modules are the source of truth.

## Structure
- `src/engines/`
  - `deployment.py`: StarkNet account deployer (supports custom constructor calldata).
  - `rescue.py`: Forced transfers and deployment helper.
  - `onramp.py`: Coinbase onramp via CCXT.
  - `gas_refuel.py`: AVNU ETH→STRK swap with dry-run support.

## 🔍 **Keywords & Tags**
- **StarkNet**: Layer 2 scaling solution for Ethereum
- **Account Deployment**: Smart contract deployment on blockchain
- **Gas Price**: Transaction fee calculation and optimization
- **Blockchain**: Distributed ledger technology
- **Web3**: Decentralized application development
- **Python**: Primary programming language
- **Rust**: Systems programming integration
- **Portfolio**: Professional project showcase
- **Post Mortem**: Industry-standard failure analysis
- **Open Source**: Community-driven development
- **Failure Analysis**: Technical and economic debugging
- **Blockchain Economics**: Gas price volatility impact
- **Smart Contract**: Deployment strategies and costs
- **Layer 2**: Ethereum scaling solutions
- **DeFi**: Decentralized finance applications
- **RPC**: Remote procedure call optimization
- **Gas Optimization**: Fee reduction strategies
- `src/core/ui/`
  - `dashboard.py`: Rich TUI dashboard (header/body/footer, logs, ROI).
- `src/foundation/`
  - Shared env loader, network oracle, security manager, constants.
- `python-logic/`
  - Thin wrappers calling core engines (activation, rescue, search, onramp, gas_refuel, chasers).
  - Deprecated stubs: `dashboard.py`, `recipe_foundry.py`, `strategy_module.py` (use core equivalents).

## Entry points
- Orchestrator: `python python-logic/orchestrator.py start` (uses core dashboard and core influence strategy; legacy fallback only if core unavailable).
- Deployment/activation: `python-logic/activate_account.py`, `force_deploy_v3.py` → core `DeploymentEngine`.
- Rescue/exit: `argent_emergency_exit.py`, `force_rescue.py`, `final_rescue_attempt.py`, `unlock_derivation.py` → core `DeploymentEngine`/`RescueEngine`/`AddressSearchEngine`.
- Onramp/refuel: `onramp.py` → `CoinbaseOnrampEngine`; `gas_refuel.py` → `GasRefuelEngine`.
- Chasers: `chaser.py` → `OrbiterBridgeAdapter`; `inflow_chaser.py` → `CdpChaserEngine`.

## Security & hygiene
- No secrets in repo; configure via `.env` (untracked). Use `foundation.legacy_env.load_env_manual` for consistent loading.
- Keys are resolved through `SecurityManager`; avoid direct env access in new code.
- Logs/artifacts are ignored via `.gitignore`; keep large files out of git.

## Usage notes
- Configure environment via `.env` (use `foundation.legacy_env.load_env_manual`).
- Sensitive keys are resolved via `SecurityManager`; avoid direct env access in new code.
- Engines support dry-run where applicable; check script flags (`--confirm`, `--no-dry-run`).
- Public/portfolio positioning: core code demonstrates Rust-Python integration, StarkNet tooling, rich TUI, and layered architecture; legacy scripts remain only as wrappers/stubs.

## Deprecations
- `python-logic/dashboard.py`: use `src/core/ui/dashboard.py`.
- `python-logic/recipe_foundry.py`: use `python-logic/unlock_derivation.py` → `engines.search.AddressSearchEngine`.
- `python-logic/strategy_module.py`: use `engines.influence.RefiningStrategy`.

## Development
- Preferred layout: core logic in `src/`, wrappers in `python-logic/`.
- Add tests under `tests/` (not yet present) and run linting/formatting before commits.
- Keep large artifacts/logs out of git; see `.gitignore`.
- For portfolio clarity: legacy helpers are marked deprecated; core modules reflect current best practices.
