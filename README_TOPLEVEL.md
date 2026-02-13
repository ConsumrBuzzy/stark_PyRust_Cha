# Repository Top-Level Layout

This document summarizes the top-level files and suggested organization for quick orientation.

## Configuration / Metadata
- `.env.example`, `.env.template` — templates for environment variables (keep real `.env` untracked).
- `pyproject.toml` — Python/Rust package metadata (maturin PyO3 module).
- `requirements.txt` — Python dependencies.
- `.gitignore`, `.github/`, `LICENSE` — git/CI/license.

## Primary Code
- `src/` — main library: engines (recovery kernel, bridge, monitoring) and foundation (state, network, security, reporting, constants).
- `rust-core/` — Rust crate for PyO3 extension (build via maturin).
- `core/` — infra utilities (RPC diagnostics, DPI bypass, UI, factory, safety).
- `python-logic/` — legacy/aux orchestration scripts.
- `tools/` — operational scripts (activation, inventory, sentry, etc.).
- `act-tools/` — auxiliary tooling.

## Entry Points
- `main.py` — primary CLI for recovery/monitoring modes.
- `scripts/` — assorted automation/testing scripts.
- Root scripts (recommend moving under `scripts/legacy/`):
  - `alchemy_tx_history.py`, `fast_phantom_search.py`, `find_ai_txs.py`, `find_phantom_txs.py`, `find_real_txs.py`, `instant_analysis.py`, `instant_tx_history.py`, `efficient_tracker.py`, `phantom_tracker.py`, `temp_orbiter_analysis.py`, `temp_phantom_all_txs.py`, `temp_phantom_search.py`, `ultra_fast_search.py`, `check_phantom_status.py`.

## Data / Logs
- `data/` — runtime state (gitignored).
- `logs/` — audit and diagnostics logs (combined_audit.log, shadow_state_check.log).

## Setup / Helpers
- `setup_venv.py`, `setup_background_monitor.ps1`, `cleanup_history.ps1` — environment/setup helpers.
- `refactor_repo.py` — README generator for hardened StarkNet infra.

## Organization Recommendations
1) Move the root utility scripts into `scripts/legacy/` (or `tools/analysis/`) and document usage in a `scripts/README.md`.
2) Keep real `.env` untracked; rely on `.env.example`/`.env.template` for configuration guidance.
3) Keep logs under `logs/` (gitignored) and remove any committed log artifacts.
4) Add a short `python-logic/README.md` to mark legacy status and main entrypoints.
5) Add a `tools/README.md` summarizing operational scripts (sentry, activation, inventory).

## Notes
- State file lives at `data/recovery_state.json` (managed by StateRegistry). It remains gitignored; consider encrypting if sensitive.
- Reporting/Network modules load env variables; ensure `.env` is populated before running CLI.
