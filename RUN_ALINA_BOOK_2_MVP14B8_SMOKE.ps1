$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B8 PREDICTION ENGINE / SMOKE ===" -ForegroundColor Cyan

python .\alina_book2_prediction_engine_mvp14b8.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14B8 prediction engine failed"
}

Write-Host "=== ALINA BOOK 2 MVP-14B8 PREDICTION ENGINE: DONE ===" -ForegroundColor Green
