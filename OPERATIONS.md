# Operations (Runbooks)

## Orchestrator
- Start TUI + strategy: `python python-logic/orchestrator.py start`
  - Uses core dashboard and core influence strategy (legacy fallback only if core unavailable).
- Pulse (single tick): `python python-logic/orchestrator.py pulse`

## Deployment / Activation
- Standard deploy: `python python-logic/activate_account.py`
- Force deploy: `python python-logic/force_deploy_v3.py`
- Emergency deploy (Argent): `python python-logic/argent_emergency_exit.py` (salt 0 then 1)
- Proxy deploy: `python python-logic/final_rescue_attempt.py` (proxy hash)

## Rescue / Transfers
- Forced extraction: `python python-logic/force_rescue.py` (uses RescueEngine)
- Derivation search: `python python-logic/unlock_derivation.py` (AddressSearchEngine)

## Onramp / Refuel / Chasers
- Coinbase onramp: `python python-logic/onramp.py` (`--no-dry-run` to send)
- AVNU refuel (ETH→STRK): `python python-logic/gas_refuel.py` (`--confirm` to send)
- Orbiter chaser (Base→StarkNet): `python python-logic/chaser.py` (`--no-dry-run` to send)
- CDP USDC chaser (gasless to transit): `python python-logic/inflow_chaser.py`

## Search / Derivation
- Expanded search: `python python-logic/expanded_search.py`
- Ultimate search: `python python-logic/ultimate_search.py`
- Salt finders: `python python-logic/salt_finder.py`, `simple_salt_finder.py`

## Environment & security
- Set `.env` (untracked) and load via `foundation.legacy_env.load_env_manual`.
- Keys resolved through `SecurityManager`; avoid direct env key usage.
- Many flows default to dry-run; use explicit flags to broadcast (`--confirm`, `--no-dry-run`).

## Logs / artifacts
- Keep logs/binaries out of git; check `.gitignore`.

## Notes
- `python-logic/` scripts are wrappers; core logic is in `src/engines` and `src/core/ui`.
- Deprecated stubs remain for compatibility: `dashboard.py`, `recipe_foundry.py`, `strategy_module.py` (do not extend).
