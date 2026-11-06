$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B2.6 CANON STORE / SMOKE ===" -ForegroundColor Cyan

python .\alina_book2_canon_store_mvp14b26.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14B2.6 canon store failed"
}

Write-Host "=== ALINA BOOK 2 MVP-14B2.6 CANON STORE: DONE ===" -ForegroundColor Green
