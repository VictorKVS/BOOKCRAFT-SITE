$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B11 QUALITY SCORECARD / SMOKE ===" -ForegroundColor Cyan

python .\alina_book2_quality_scorecard_mvp14b11.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14B11 quality scorecard failed"
}

Write-Host "=== ALINA BOOK 2 MVP-14B11 QUALITY SCORECARD: DONE ===" -ForegroundColor Green
