# Contributing

Welcome! This project is public/portfolio-ready. Core logic lives in `src/`; `python-logic/` scripts are thin wrappers or deprecated stubs. Please keep changes clean, secure, and focused.

## Setup
- Python 3.12+
- Rust toolchain (for PyO3/maturin if rebuilding Rust components)
- Install deps: `pip install -r requirements.txt`
- Load env from `.env` (untracked) using `foundation.legacy_env.load_env_manual()`

## Core layout
- `src/engines/`: deployment, rescue, onramp, gas_refuel, search, influence, bridge_system, cdp_chaser
- `src/core/ui/`: Rich dashboard
- `src/foundation/`: env loader, network oracle, security manager, constants
- `python-logic/`: wrappers to core engines; legacy stubs are deprecated

## Coding guidelines
- Prefer core modules; avoid adding new logic to `python-logic/`.
- Use type hints, async for network/chain calls when possible.
- Use `SecurityManager` for keys; do not access raw secrets directly.
- Keep dry-run flags intact and default-safe where applicable.
- Imports: prefer absolute imports from core packages.

## Security & hygiene
- No secrets in git; configure via `.env` (untracked).
- Do not log sensitive material; validate addresses/class hashes before deploy.
- Keep logs/binaries/artifacts out of git (`.gitignore` enforced).

## Testing & quality
- Add tests under `tests/` (not yet populated).
- Run linters/formatters before committing (ruff/black/isort if available).
- Keep PRs focused; avoid unrelated changes in the same commit.

## Running key flows
- Orchestrator (core UI + influence): `python python-logic/orchestrator.py start`
- Deployment/activation: `python-logic/activate_account.py` / `force_deploy_v3.py`
- Rescue/exit: `argent_emergency_exit.py`, `force_rescue.py`, `final_rescue_attempt.py`, `unlock_derivation.py`
- Onramp/refuel: `onramp.py`, `gas_refuel.py`
- Chasers: `chaser.py`, `inflow_chaser.py`

## Documentation
- `README.md`: project overview, structure, entry points, deprecations
- `.windsurf/rules.md`: repo rules for editors (core-first, security hygiene)

Thank you for contributing responsibly!
