$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 REAL LLM WRITER MVP-02 ===" -ForegroundColor Cyan
Write-Host "PROGRESS: 50% -> target 65%" -ForegroundColor Yellow

python .\run_real_llm_writer_mvp02.py
if ($LASTEXITCODE -ne 0) {
    throw "ALINA BOOK 2 Real LLM Writer MVP-02 failed"
}

Write-Host "=== ALINA BOOK 2 REAL LLM WRITER MVP-02: PASS ===" -ForegroundColor Green
Write-Host "PROGRESS AFTER PHYSICAL PASS: 65%" -ForegroundColor Green
