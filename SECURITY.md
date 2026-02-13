# Security

## Secrets
- Never commit secrets. Use `.env` (untracked) and load via `foundation.legacy_env.load_env_manual`.
- Resolve keys through `SecurityManager`; avoid direct env access in new code.

## Logging
- Do not log raw secrets or full private keys. Truncate where necessary.
- Prefer Rich/loguru/stdout with safe content.

## Deployments & transactions
- Default to dry-run where supported; require explicit `--confirm` or equivalent for live operations.
- Validate addresses/class hashes/salts before deployment.

## Repo hygiene
- `.gitignore` excludes logs, artifacts, and binaries. Keep large files and generated outputs out of git.
- Legacy scripts are wrappers or stubs; core engines (`src/engines`) are the source of truth.

## Dependencies
- Prefer pinned versions (see `requirements.txt`/`pyproject`); remove unused deps.
- Keep Rust toolchain up to date when rebuilding PyO3 components.

## Public/portfolio stance
- Code is safe for public view: no secrets in repo, deprecations noted, core-first architecture documented.
- Review contributions for secret leaks and unnecessary scope (keep PRs small and focused).
