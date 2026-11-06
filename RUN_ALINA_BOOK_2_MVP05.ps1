$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 FULL STORY CONTINUATION MVP-05 ===" -ForegroundColor Cyan
Write-Host "PROGRESS: 85% -> target 93%" -ForegroundColor Yellow

python .\run_full_story_continuation_mvp05.py
if ($LASTEXITCODE -ne 0) {
    throw "ALINA BOOK 2 Full Story Continuation MVP-05 failed"
}

Write-Host "=== ALINA BOOK 2 FULL STORY CONTINUATION MVP-05: PASS ===" -ForegroundColor Green
Write-Host "PROGRESS AFTER PHYSICAL PASS: 93%" -ForegroundColor Green
