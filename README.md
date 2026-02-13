# stark_PyRust_Chain

Public/portfolio-ready refactor with Python 3.12 + Rust (PyO3) engines. Legacy `python-logic/` scripts are thin wrappers or deprecated stubs; core modules are the source of truth.

## Structure
- `src/engines/`
  - `deployment.py`: StarkNet account deployer (supports custom constructor calldata).
  - `rescue.py`: Forced transfers and deployment helper.
  - `onramp.py`: Coinbase onramp via CCXT.
  - `gas_refuel.py`: AVNU ETH→STRK swap with dry-run support.
  - `search.py`: Address/class-hash/salt search utilities.
  - `influence.py`: Core influence strategy.
  - `bridge_system.py`: Bridge systems + `OrbiterBridgeAdapter`.
  - `cdp_chaser.py`: Coinbase CDP gasless USDC chaser.
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
