# Architecture

## Overview
- **Language/stack:** Python 3.12 + Rust (PyO3) extension (`stark_pyrust_chain`), Rich for CLI/TUI, Loguru/stdout logging, async networking.
- **Structure:**
  - `src/engines/`: business logic (deployment, rescue, onramp, gas refuel, search, influence, bridge/orbiter, cdp chaser).
  - `src/core/ui/`: Rich TUI dashboard (header/body/footer, logs, ROI).
  - `src/foundation/`: env loader, network oracle, security manager, constants.
  - `python-logic/`: thin wrappers around engines; deprecated stubs only for backward compatibility.

## Key modules
- **DeploymentEngine (`src/engines/deployment.py`)**
  - Deploys StarkNet accounts (deploy_account_v3), supports custom constructor calldata.
  - Uses `SecurityManager` for keys and `NetworkOracle` for clients; validates computed vs target address.
- **RescueEngine (`src/engines/rescue.py`)**
  - Forced transfers (`force_transfer` with resource bounds) and deploy helper via DeploymentEngine.
- **Bridge/Chaser**
  - `OrbiterBridgeAdapter` (`bridge_system.py`): Base→StarkNet chaser with amount encoding/destination code.
  - `cdp_chaser.py`: Coinbase CDP gasless USDC to transit wallet.
- **Onramp/Refuel**
  - `onramp.py`: Coinbase onramp via CCXT, dry-run/live.
  - `gas_refuel.py`: AVNU ETH→STRK swap builder/executor; dry-run by default.
- **Search/Derivation**
  - `search.py`: class-hash/salt search, custom salts/patterns supported.
- **Influence Strategy**
  - `influence.py`: core RefiningStrategy (replaces legacy `strategy_module`).
- **UI**
  - `src/core/ui/dashboard.py`: Rich TUI; orchestrator prefers this over legacy dashboard.

## Environment & security
- Load env via `foundation.legacy_env.load_env_manual` (UTF-8/latin-1 fallback, alias mapping).
- Secrets resolved through `SecurityManager`; avoid direct env key usage in new code.
- `.env` is untracked; no secrets in repo. `.gitignore` excludes logs/binaries.

## Orchestrator
- Entry: `python-logic/orchestrator.py start`
  - Prefers core dashboard and core influence strategy, with legacy fallback only if core unavailable.
  - Monkey-patches strategy log to feed dashboard log/ROI.

## Deployment pathways
- Activation/deploy wrappers (`activate_account.py`, `force_deploy_v3.py`) call DeploymentEngine.
- Rescue/exit wrappers call DeploymentEngine/RescueEngine and AddressSearchEngine for derivation.
- Onramp/refuel/chasers wrap onramp, gas_refuel, Orbiter/COINBASE CDP engines.

## Deprecated legacy
- `python-logic/dashboard.py`, `recipe_foundry.py`, `strategy_module.py` are stubs; use core equivalents.

## Testing & quality (current gap)
- `tests/` not yet populated; add unit/integration tests for engines and orchestrator flows.
- Suggested tools: ruff/black/isort, mypy/pyright.
