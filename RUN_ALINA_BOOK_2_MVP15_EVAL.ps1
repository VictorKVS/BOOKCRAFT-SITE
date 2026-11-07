$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-15 EVALUATION BENCHMARK / SMOKE ===" -ForegroundColor Cyan

python .\alina_book2_evaluation_benchmark_mvp15.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-15 evaluation benchmark failed"
}

Write-Host "=== ALINA BOOK 2 MVP-15 EVALUATION BENCHMARK: DONE ===" -ForegroundColor Green
