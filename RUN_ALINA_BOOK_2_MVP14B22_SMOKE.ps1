$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:ALINA_MAX_CHUNKS = "3"
try {
    Write-Host "=== ALINA BOOK 2 MVP-14B2.2 NARRATIVE MODE GUARD / SMOKE ===" -ForegroundColor Cyan
    python .\alina_book2_narrative_guard_mvp14b22.py
    if ($LASTEXITCODE -ne 0) { throw "MVP-14B2.2 narrative mode guard failed" }
} finally {
    Remove-Item Env:ALINA_MAX_CHUNKS -ErrorAction SilentlyContinue
}
Write-Host "=== ALINA BOOK 2 MVP-14B2.2 NARRATIVE MODE GUARD: DONE ===" -ForegroundColor Green
