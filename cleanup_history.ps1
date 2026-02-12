# stark_PyRust_Chain History Scrub Utility (ADR-044)
# warning: This script REWRITES your git history.

Write-Host "[WARN] ADR-044: Secure History Sanitization Protocol" -ForegroundColor Yellow
Write-Host "This will permanently remove .env and vault.bin from all commits." -ForegroundColor Yellow
$confirmation = Read-Host "Are you sure you want to proceed? (y/n)"

if ($confirmation -ne "y") {
    Write-Host "Aborted."
    exit
}

# 1. Install git-filter-repo
Write-Host "`n[+] Installing git-filter-repo..." -ForegroundColor Cyan
try {
    pip install git-filter-repo
}
catch {
    Write-Host "[!] Failed to install git-filter-repo. Ensure Python/Pip is in PATH." -ForegroundColor Red
    exit 1
}

# 2. Execute Scrub
Write-Host "`n[+] Scrubbing Sensitive Files..." -ForegroundColor Cyan
# Using --force because we are running this on the active repo
try {
    git filter-repo --path .env --path rust-core/vault.bin --invert-paths --force
}
catch {
    Write-Host "[!] git-filter-repo failed. Ensure you are in the repo root." -ForegroundColor Red
    exit 1
}

# 3. Garbage Collection
Write-Host "`n[+] Running Garbage Collection..." -ForegroundColor Cyan
git reflog expire --expire=now --all
git gc --prune=now --aggressive

Write-Host "`n[OK] History Scrub Complete!" -ForegroundColor Green
Write-Host "Your local repository is now clean of legacy secrets."
Write-Host "`n[NEXT] FINAL STEP:" -ForegroundColor Magenta
Write-Host "Run: git push origin --force --all"
Write-Host "This will overwrite the remote repository with the clean history."
