---
description: tools directory refactor plan
---

# Tools Directory Refactor Plan

## Goals
- Eliminate duplicated env/path logic and hardcoded addresses/gas thresholds.
- Consolidate network/reporting/security helpers into ops/core modules.
- Preserve existing CLI entrypoints (tools/*) while moving logic into reusable ops components.
- Fix known bugs (e.g., literal env strings) and reduce direct starknet_py/Web3 surface where core provides equivalents.

## Current Issues (high-level)
- Many scripts load .env and mutate sys.path individually.
- Hardcoded addresses/thresholds; some incorrectly quoted (e.g., "os.getenv(...)" literals).
- Direct starknet_py/Web3 usage instead of core `src.foundation.network` / `ops.network_checks`.
- Ad-hoc Telegram/requests instead of `ops.reporting_ops`.
- Ghost/activation logic duplicated across multiple scripts.

## Target Shared Modules
- `ops.env`: already exists; extend with ghost/activation thresholds if needed.
- `ops.network_checks`: reuse for balances/gas where possible; extend for StarkNet ERC-20 balance helper if needed.
- `ops.reporting_ops`: standard alerts/pulses instead of raw requests.
- New modules to add:
  - `ops.activation`: wrap account activation (from tools/activate.py) including dry-run connectivity.
  - `ops.audit`: shared StarkNet balance + deployment checks (for audit.py/combined_audit.py).
  - `ops.ghost_monitor`: ghost detection/sweep readiness, RPC rotation, threshold logic (for legacy_sentry*, rescue, orbiter_checker).
  - `ops.portfolio`: provider interfaces + reporting from inventory.py (swap mocks later if real providers available).
  - `ops.security_reset`: interactive security reset/verify wrapping core.safety.EncryptedSigner (from reset_security.py).

## File-by-File Notes (non-legacy)
- activate.py: StarkNet account activation via starknet_py. Move core logic to `ops.activation`, keep CLI wrapper.
- audit.py: StarkNet balance/deployment audit via starknet_py; bug: main_wallet set to string literal. Move to `ops.audit`; fix env bug; use ops.env addresses and reporting.
- combined_audit.py: Continuous balance aggregator (main/ghost), thresholds 0.016/0.005, file logging, reports. Fold into `ops.audit` (and ghost monitor if needed) with configurable thresholds.
- inventory.py: Multi-chain inventory with mock providers, Pydantic PortfolioSummary, Rich/Markdown report. Move provider interfaces/reporting into `ops.portfolio`; keep CLI thin.
- legacy_sentry.py: Ghost monitoring + sweep via rescue_funds; path/env hacks; thresholds hardcoded. Consolidate into `ops.ghost_monitor`.
- legacy_sentry_v2.py: Ghost monitoring with RPC rotation; Telegram via requests; literal env strings. Consolidate into `ops.ghost_monitor`; fix env usage and use reporting_ops.
- orbiter_checker.py: Checks fixed Base tx + StarkNet ghost balance with literal env strings. Wrap into ghost monitor diagnostics.
- rescue.py: Ghost sweep/recovery with RPC rotation; uses strategy_module; literal env strings. Merge useful pieces into `ops.ghost_monitor` and deprecate CLI or keep wrapper.
- reset_security.py: Interactive password reset/verification using core.safety.EncryptedSigner. Move logic to `ops.security_reset`, keep CLI prompt.
- self_fund_pipeline.py, simple_check.py, starkscan_scraper.py, voyager_scraper.py, war_room_dashboard.py, verify_ghost.py, test_inventory.py: Not yet refactored; expect env/path duplication; plan to review and route into appropriate ops modules (portfolio/audit/ghost_monitor).

## Legacy folder (tools/legacy/)
- Assorted checks/build/debug (account_check, brute_force_account, monitor_activation, verify_gas, etc.). Treat as deprecated; only uplift specific flows if still needed (ghost monitoring/activation diagnostics). Otherwise keep archived.

## Proposed Phased Refactor
1) Ghost/Recovery Stack
   - Create `ops.ghost_monitor` with: env-driven ghost/main addresses and thresholds; RPC rotation helper; balance check (ERC-20 balanceOf); sweep planning hooks; optional Telegram via reporting_ops.
   - Migrate `legacy_sentry.py`, `legacy_sentry_v2.py`, `rescue.py`, `orbiter_checker.py` to thin wrappers calling ghost_monitor. Fix literal env string bugs in the process.

2) Activation & Audits
   - Create `ops.activation` from `activate.py` (dry-run + deploy). Keep CLI wrapper.
   - Create `ops.audit` for StarkNet balance/deployment (use foundation.network or direct starknet_py where needed). Refactor `audit.py` (fix main wallet env) and `combined_audit.py` into wrappers calling ops.audit.

3) Portfolio/Inventory
   - Create `ops.portfolio` with provider interfaces and report formatting from `inventory.py`; allow real providers later. CLI stays as thin wrapper.

4) Security Utilities
   - Create `ops.security_reset` for password reset/verify logic from `reset_security.py`; keep CLI prompt wrapper.

5) Cleanup & Tests
   - Remove duplicated .env loaders and sys.path hacks in tools/ wrappers; rely on ops.env load in modules.
   - Add pytest for new ops modules (ghost_monitor, activation, audit, portfolio, security_reset) with stubs/mocks.
   - Mark legacy/ as deprecated in README; optionally add NOTICE in legacy scripts.

## Known Bugs to Fix During Refactor
- audit.py: `self.main_wallet = "os.getenv("STARKNET_WALLET_ADDRESS")"` should use env value.
- legacy_sentry_v2.py / rescue.py / orbiter_checker.py: literal env strings for ghost/eth contract; must parse env properly.
- General: replace hardcoded thresholds with OpsConfig overrides.

## Acceptance Criteria
- All tools/ CLIs delegate to ops modules; no sys.path hacks or ad-hoc .env parsing in wrappers.
- Addresses/thresholds configurable via OpsConfig/env; no literal env strings remain.
- Ghost monitoring/activation/audit flows use shared network/reporting helpers where feasible.
- New ops modules covered by smoke tests; existing ops tests remain green (`pytest tests/test_ops_*`).
- Documentation: update tools/README.md to reflect new ops architecture and deprecated legacy/ folder.
