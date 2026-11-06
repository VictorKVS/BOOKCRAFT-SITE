$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B10 LEARNING & CALIBRATION / SMOKE ===" -ForegroundColor Cyan

python .\alina_book2_learning_calibration_mvp14b10.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14B10 learning/calibration failed"
}

Write-Host "=== ALINA BOOK 2 MVP-14B10 LEARNING & CALIBRATION: DONE ===" -ForegroundColor Green
