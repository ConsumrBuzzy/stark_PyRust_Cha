# python-logic (legacy/aux workflows)

This directory contains legacy or auxiliary orchestration scripts for StarkNet/Base workflows (activation, rescue, bridge, search). They predate the consolidated `src/` engines/ foundation modules and are kept for compatibility/testing.

Guidance:
- Prefer using `main.py` (RecoveryKernel) and `src/` modules for new flows.
- When updating these scripts, share logic via `src/` to avoid duplication.
- Ensure configuration comes from environment variables or `.env` (untracked).
- Add a short usage header to each script you actively maintain.
