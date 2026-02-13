# Testing

## Status
- Test suite not yet populated. Add unit/integration tests for engines and orchestrator flows.

## Recommendations
- Framework: `pytest`
- Lint/format: `ruff` / `black` / `isort`
- Type check: `mypy` or `pyright`
- Coverage: `pytest --cov=src`

## Suggested test areas
- DeploymentEngine: address validation, constructor calldata, resource bounds.
- RescueEngine: force_transfer happy path and low-balance failure.
- Onramp/Gas refuel: dry-run vs confirm flag behavior; payload building.
- Search: custom salts/patterns; match/no-match cases.
- Influence strategy: tick behavior (dry-run), logging hook integration.
- Orbiter/Coinbase chasers: dry-run payload, balance checks, error paths.
- UI: smoke test dashboard render (non-interactive) to ensure layout builds.

## Running
```bash
pytest
```
Add options (lint/type) once configured:
```bash
ruff check .
black --check .
isort --check-only .
mypy src
```
