$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 REAL STORY INGEST MVP-04 ===" -ForegroundColor Cyan
Write-Host "PROGRESS: 75% -> target 85%" -ForegroundColor Yellow

python .\run_story_ingest_mvp04.py
if ($LASTEXITCODE -ne 0) {
    throw "ALINA BOOK 2 Real Story Ingest MVP-04 failed"
}

Write-Host "=== ALINA BOOK 2 REAL STORY INGEST MVP-04: PASS ===" -ForegroundColor Green
Write-Host "PROGRESS AFTER PHYSICAL PASS: 85%" -ForegroundColor Green
