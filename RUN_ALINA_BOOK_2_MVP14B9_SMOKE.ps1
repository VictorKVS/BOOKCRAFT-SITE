$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B9 BACKTESTING ENGINE / SMOKE ===" -ForegroundColor Cyan

python .\alina_book2_backtesting_engine_mvp14b9.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14B9 backtesting engine failed"
}

Write-Host "=== ALINA BOOK 2 MVP-14B9 BACKTESTING ENGINE: DONE ===" -ForegroundColor Green
