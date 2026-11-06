$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:ALINA_MAX_CHUNKS = "3"
try {
    Write-Host "=== ALINA BOOK 2 MVP-14B2.1 EVIDENCE CRITIC / SMOKE ===" -ForegroundColor Cyan
    python .\alina_book2_evidence_critic_mvp14b21.py
    if ($LASTEXITCODE -ne 0) { throw "MVP-14B2.1 evidence critic failed" }
} finally {
    Remove-Item Env:ALINA_MAX_CHUNKS -ErrorAction SilentlyContinue
}
Write-Host "=== ALINA BOOK 2 MVP-14B2.1 EVIDENCE CRITIC: DONE ===" -ForegroundColor Green
