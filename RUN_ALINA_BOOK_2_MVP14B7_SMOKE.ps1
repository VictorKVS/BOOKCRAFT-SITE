$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B7 HYPOTHESIS ENGINE / SMOKE ===" -ForegroundColor Cyan

python .\alina_book2_hypothesis_engine_mvp14b7.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14B7 hypothesis engine failed"
}

Write-Host "=== ALINA BOOK 2 MVP-14B7 HYPOTHESIS ENGINE: DONE ===" -ForegroundColor Green
