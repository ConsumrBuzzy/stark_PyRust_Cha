# Changelog

## [2026-02-13] - 🚨 CRITICAL: Project Retirement
- **CRITICAL**: 0.014863 ETH (~$52 USD) locked in undeployed StarkNet account
- **Total Loss**: $63 USD (including bridge fees and failed attempts)
- **Issue**: Cannot deploy account due to extreme gas prices (~42,000 Gwei)
- **Deployment Cost**: ~24 ETH (not feasible with current balance)
- **Status**: Funds permanently locked, project retired
- **Documentation**: Added comprehensive situation report and post mortem analysis
- **Impact**: Account cannot send transactions or transfer funds
- **Retirement**: Project retired, open to community fork
- **Legacy**: Complete failure analysis for community learning

## [Unreleased]
- Add tests under `tests/` (currently empty).
- Add lint/type tooling (ruff/black/isort, mypy/pyright) to CI.

## [Refactor: Core Engines & Cleanup]
- Migrated legacy `python-logic/` scripts into core engines:
  - DeploymentEngine (custom constructor calldata), RescueEngine, Onramp, GasRefuel, Search, Influence, Bridge/Orbiter, CDP chaser.
- Added core Rich TUI: `src/core/ui/dashboard.py`; orchestrator prefers core UI/strategy.
- Created shared env/security/network foundation modules.
- Stubs/deprecations: legacy `dashboard.py`, `recipe_foundry.py`, `strategy_module.py` now point to core equivalents.
- Added doc set: README, CONTRIBUTING, ARCHITECTURE, SECURITY, TESTING, OPERATIONS, Windsurf rules.

## [Security & hygiene]
- No secrets in repo; `.env` loading unified via `foundation.legacy_env.load_env_manual`.
- Key handling through `SecurityManager`; dry-run defaults preserved.
- `.gitignore` updated for logs/artifacts/binaries.
