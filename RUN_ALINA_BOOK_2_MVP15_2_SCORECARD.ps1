$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "=== ALINA BOOK 2 MVP-15.2 FULL EVALUATION SCORECARD ===" -ForegroundColor Cyan
python .\alina_book2_full_evaluation_scorecard_mvp152.py
if ($LASTEXITCODE -ne 0) { throw "MVP-15.2 full evaluation scorecard failed" }
Write-Host "=== ALINA BOOK 2 MVP-15.2 FULL EVALUATION SCORECARD: DONE ===" -ForegroundColor Green
