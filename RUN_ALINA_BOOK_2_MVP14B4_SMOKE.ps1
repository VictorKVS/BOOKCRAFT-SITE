$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B4 TEMPORAL MODEL / SMOKE ===" -ForegroundColor Cyan

python .\alina_book2_temporal_model_mvp14b4.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14B4 temporal model failed"
}

Write-Host "=== ALINA BOOK 2 MVP-14B4 TEMPORAL MODEL: DONE ===" -ForegroundColor Green
