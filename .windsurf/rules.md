---
description: Windsurf rules for stark_PyRust_Chain
---

# Windsurf Rules (Public/Portfolio Repo)

## Core principles
- Core engines are the source of truth: prefer `src/engines/` and `src/core/ui/`; `python-logic/` scripts are wrappers or deprecated stubs.
- No secrets in git: load config via `.env` using `foundation.legacy_env.load_env_manual`; never hardcode keys.
- Use `SecurityManager` for key resolution; avoid direct env access in new code.
- Keep the repo clean: no logs/artifacts/binaries in git; respect `.gitignore`.

## File ownership
- Engines: `src/engines/*` (deployment, rescue, onramp, gas_refuel, search, influence, bridge_system, cdp_chaser).
- UI: `src/core/ui/dashboard.py` (Rich TUI). Prefer this over legacy `python-logic/dashboard.py`.
- Wrappers: `python-logic/*` scripts call core engines; legacy stubs remain only for backward compatibility.
- Foundation: env/network/security/constants in `src/foundation/`.

## Coding conventions
- Python 3.12, use type hints; prefer async where applicable (network/chain calls).
- Logging/UX: Rich for CLI/TUI, Loguru or stdout for scripts; keep dry-run flags intact.
- Security: never print full secrets; validate addresses/class hashes/salts before deploy; use dry-run defaults where possible.
- Imports: prefer absolute imports from core modules; avoid modifying sys.path outside wrappers.

## UI/UX
- Use `src/core/ui/dashboard.py` for TUI; if extending, keep header/body/footer pattern, logs, ROI.
- Do not expand legacy UI; mark any new legacy UI as deprecated.

## Tests/quality
- Add tests under `tests/`; run lint/format before commit (ruff/black/isort if configured).
- Keep changes scoped; avoid touching multiple concerns in one PR.

## Public/portfolio positioning
- Document new features in README; highlight core/Rust-Py integration and StarkNet tooling.
- Keep repo safe for public viewing: no secrets, no noisy artifacts, clear deprecation notes.
