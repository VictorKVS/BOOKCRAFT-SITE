$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "=== ALINA BOOK 2 MVP-15.1 HISTORICAL FORECAST BASELINE ===" -ForegroundColor Cyan
python .\alina_book2_historical_forecast_baseline_mvp151.py
if ($LASTEXITCODE -ne 0) { throw "MVP-15.1 historical forecast baseline failed" }
Write-Host "=== ALINA BOOK 2 MVP-15.1 HISTORICAL FORECAST BASELINE: DONE ===" -ForegroundColor Green
