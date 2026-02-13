# Scripts

This folder contains operational and helper scripts. Primary structure:

- `legacy/` — ad-hoc/analysis utilities migrated from the repo root (TX history, trackers, temp searches). Treat as legacy; prefer invoking main CLI (`main.py`) for standard workflows.
- `setup/` — environment and maintenance helpers (PowerShell setup/cleanup).

Guidance:
- Keep new scripts organized by domain (e.g., `analysis/`, `ops/`) instead of the repo root.
- Ensure secrets come from environment variables or `.env` (untracked); do not hardcode credentials.
- Prefer wrapping shared logic into `src/` modules and calling from these scripts to avoid duplication.
