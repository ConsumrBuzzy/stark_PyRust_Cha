# tools

Operational scripts for StarkNet/Base infrastructure (activation, monitoring, inventory, sentry). These are intended for operator use and should rely on shared logic from `src/` when possible.

Suggested usage:
- Keep scripts small and delegate reusable code to `src/` modules.
- Document required environment variables at the top of each script.
- Logging should go to `logs/` (gitignored) and avoid secrets.
- Add new tools under subfolders if they grow (e.g., `monitoring/`, `activation/`, `inventory/`).
