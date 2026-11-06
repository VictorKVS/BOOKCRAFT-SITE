$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 MVP-14B6 STATE TRANSITION & CAUSAL / SMOKE ===" -ForegroundColor Cyan

python .\alina_book2_state_transition_causal_mvp14b6.py
if ($LASTEXITCODE -ne 0) {
    throw "MVP-14B6 state transition / causal layer failed"
}

Write-Host "=== ALINA BOOK 2 MVP-14B6 STATE TRANSITION & CAUSAL: DONE ===" -ForegroundColor Green
