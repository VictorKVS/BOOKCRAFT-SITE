$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "=== ALINA BOOK 2 PRODUCTION LOOP MVP-01 ===" -ForegroundColor Cyan

python .\run_production_loop_mvp01.py
if ($LASTEXITCODE -ne 0) {
    throw "ALINA BOOK 2 Production Loop MVP-01 failed"
}

Write-Host "=== ALINA BOOK 2 PRODUCTION LOOP MVP-01: PASS ===" -ForegroundColor Green
