$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B2.5 CANON ADMISSION / SMOKE ===" -ForegroundColor Cyan

python .\alina_book2_canon_admission_mvp14b25.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14B2.5 canon admission failed"
}

Write-Host "=== ALINA BOOK 2 MVP-14B2.5 CANON ADMISSION: DONE ===" -ForegroundColor Green
