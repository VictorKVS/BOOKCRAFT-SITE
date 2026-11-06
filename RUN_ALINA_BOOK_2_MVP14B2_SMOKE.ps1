$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:ALINA_MAX_CHUNKS = "3"
try {
    Write-Host "=== ALINA BOOK 2 MVP-14B2 SMOKE / FIRST 3 PRIMARY CHUNKS ===" -ForegroundColor Cyan
    python .\alina_book2_claims_mvp14b2.py
    if ($LASTEXITCODE -ne 0) { throw "MVP-14B2 smoke failed" }
} finally {
    Remove-Item Env:ALINA_MAX_CHUNKS -ErrorAction SilentlyContinue
}
Write-Host "=== ALINA BOOK 2 MVP-14B2 SMOKE: DONE ===" -ForegroundColor Green
