$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B5 STATE ENGINE / SMOKE ===" -ForegroundColor Cyan

python .\alina_book2_state_engine_mvp14b5.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14B5 state engine failed"
}

Write-Host "=== ALINA BOOK 2 MVP-14B5 STATE ENGINE: DONE ===" -ForegroundColor Green
