$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B3 CONTRADICTION ENGINE / SMOKE ===" -ForegroundColor Cyan

python .\alina_book2_contradiction_engine_mvp14b3.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14B3 contradiction engine failed"
}

Write-Host "=== ALINA BOOK 2 MVP-14B3 CONTRADICTION ENGINE: DONE ===" -ForegroundColor Green
