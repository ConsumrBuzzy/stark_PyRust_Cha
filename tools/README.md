# tools

Operational scripts for StarkNet/Base infrastructure (activation, monitoring, inventory, sentry).

Current architecture:
- Core logic now lives in `src/ops/*` (activation, audit, ghost_monitor, portfolio, security_reset).
- CLI entrypoints in `tools/` are thin wrappers that delegate to ops modules.
- Ghost/recovery scripts (legacy_sentry*, orbiter_checker, rescue) now use `ops.ghost_monitor`.
- Activation/Audit/Inventory/Security reset use `ops.activation`, `ops.audit_ops`, `ops.portfolio`, `ops.security_reset`.

Guidance:
- Keep scripts small; add new logic to `src/ops/` and import from wrappers.
- Document required environment variables at the top of new ops modules (not in wrappers).
- Logging should go to `logs/` (gitignored) and avoid secrets.
- Add new tools under subfolders if they grow (e.g., `monitoring/`, `activation/`, `inventory/`).

Legacy notice:
- `tools/legacy/` scripts are deprecated; prefer the ops-based wrappers above.
