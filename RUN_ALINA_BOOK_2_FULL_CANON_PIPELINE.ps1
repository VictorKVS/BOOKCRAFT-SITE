$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Remove-Item Env:ALINA_MAX_CHUNKS -ErrorAction SilentlyContinue

# Proven thermal policy from earlier ALINA full runs.
$env:ALINA_THERMAL_PAUSE_C = "90"
$env:ALINA_THERMAL_RESUME_C = "75"
$env:ALINA_THERMAL_POLL_SEC = "10"
$env:ALINA_OLLAMA_TIMEOUT_SEC = "600"
$env:ALINA_OLLAMA_RETRIES = "3"

function Invoke-AlinaStage {
    param(
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$true)][string]$Script
    )
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor DarkGray
    Write-Host "START $Name" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor DarkGray

    python $Script
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }

    Write-Host "PASS $Name" -ForegroundColor Green
}

Write-Host "=== ALINA BOOK 2 / FULL CLAIM-TO-SAFE-CANON PIPELINE ===" -ForegroundColor Cyan
Write-Host "WORK: Сто лет тому вперед (Гостья из будущего)"
Write-Host "EXPECTED PRIMARY CHUNKS: 61"
Write-Host "THERMAL: pause >= $env:ALINA_THERMAL_PAUSE_C C; resume <= $env:ALINA_THERMAL_RESUME_C C"

Invoke-AlinaStage "MVP-14B2 CLAIM EXTRACTION" ".\alina_book2_claims_mvp14b2.py"
Invoke-AlinaStage "MVP-14B2.1 EVIDENCE ENTAILMENT CRITIC" ".\alina_book2_evidence_critic_mvp14b21.py"
Invoke-AlinaStage "MVP-14B2.2 NARRATIVE MODE GUARD" ".\alina_book2_narrative_guard_mvp14b22.py"
Invoke-AlinaStage "MVP-14B2.3 CONTEXT PRECISION GATE" ".\alina_book2_precision_gate_mvp14b23.py"
Invoke-AlinaStage "MVP-14B2.4 DETERMINISTIC CANON SAFETY" ".\alina_book2_deterministic_safety_mvp14b24.py"

$claimFiles = Get-ChildItem ".\projects\sto_let_tomu_vpered\evidence\chunk_claims_v2\primary-*.json" -ErrorAction Stop
if ($claimFiles.Count -ne 61) {
    throw "Expected 61 claim files, found $($claimFiles.Count)"
}

$required = @(
    ".\projects\sto_let_tomu_vpered\runs\mvp14b2_claim_level_canon.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b2_1_evidence_critic.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b2_2_narrative_mode_guard.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b2_3_canon_precision_gate.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b2_4_deterministic_canon_safety.json"
)
foreach ($p in $required) {
    if (-not (Test-Path $p)) {
        throw "Missing required run artifact: $p"
    }
}

Write-Host ""
Write-Host "PASS primary_claim_files: 61" -ForegroundColor Green
Write-Host "PASS all_stage_run_artifacts_exist" -ForegroundColor Green
Write-Host "=== ALINA BOOK 2 FULL CLAIM-TO-SAFE-CANON PIPELINE: PHYSICAL EXECUTION COMPLETE ===" -ForegroundColor Green
Write-Host "NOTE: execution completion is NOT semantic final acceptance. Publish and audit results next." -ForegroundColor Yellow
