$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Remove-Item Env:ALINA_MAX_CHUNKS -ErrorAction SilentlyContinue

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

Write-Host "=== ALINA BOOK 2 / FULL TRUSTED ANALYTICAL PIPELINE ===" -ForegroundColor Cyan
Write-Host "WORK_ID: sto_let_tomu_vpered"
Write-Host "EXPECTED PRIMARY CHUNKS: 61"
Write-Host "THERMAL: pause >= $env:ALINA_THERMAL_PAUSE_C C; resume <= $env:ALINA_THERMAL_RESUME_C C"

# ---------------------------------------------------------------------
# PHASE A - CLAIM EXTRACTION AND CANON SAFETY
# ---------------------------------------------------------------------
Invoke-AlinaStage "MVP-14B2 CLAIM EXTRACTION" ".\alina_book2_claims_mvp14b2.py"
Invoke-AlinaStage "MVP-14B2.1 EVIDENCE ENTAILMENT CRITIC" ".\alina_book2_evidence_critic_mvp14b21.py"
Invoke-AlinaStage "MVP-14B2.2 NARRATIVE MODE GUARD" ".\alina_book2_narrative_guard_mvp14b22.py"
Invoke-AlinaStage "MVP-14B2.3 CONTEXT PRECISION GATE" ".\alina_book2_precision_gate_mvp14b23.py"
Invoke-AlinaStage "MVP-14B2.4 DETERMINISTIC CANON SAFETY" ".\alina_book2_deterministic_safety_mvp14b24.py"
Invoke-AlinaStage "MVP-14B2.5 CANON ADMISSION" ".\alina_book2_canon_admission_mvp14b25.py"

# ---------------------------------------------------------------------
# PHASE B - TRUSTED STORES AND GRAPH
# ---------------------------------------------------------------------
Invoke-AlinaStage "MVP-14B2.6 CANON STORE" ".\alina_book2_canon_store_mvp14b26.py"
Invoke-AlinaStage "MVP-14B2.7 ENTITY REGISTRY" ".\alina_book2_entity_registry_mvp14b27.py"
Invoke-AlinaStage "MVP-14B2.8 RELATION AND EVENT STORE" ".\alina_book2_relation_event_store_mvp14b28.py"
Invoke-AlinaStage "MVP-14B2.9 KNOWLEDGE GRAPH ASSEMBLY" ".\alina_book2_knowledge_graph_mvp14b29.py"

# ---------------------------------------------------------------------
# PHASE C - ANALYTICAL REASONING
# ---------------------------------------------------------------------
Invoke-AlinaStage "MVP-14B3 CONTRADICTION ENGINE" ".\alina_book2_contradiction_engine_mvp14b3.py"
Invoke-AlinaStage "MVP-14B4 TEMPORAL MODEL" ".\alina_book2_temporal_model_mvp14b4.py"
Invoke-AlinaStage "MVP-14B5 STATE ENGINE" ".\alina_book2_state_engine_mvp14b5.py"
Invoke-AlinaStage "MVP-14B6 STATE TRANSITION AND CAUSAL LAYER" ".\alina_book2_state_transition_causal_mvp14b6.py"
Invoke-AlinaStage "MVP-14B7 HYPOTHESIS ENGINE" ".\alina_book2_hypothesis_engine_mvp14b7.py"
Invoke-AlinaStage "MVP-14B8 PREDICTION ENGINE" ".\alina_book2_prediction_engine_mvp14b8.py"
Invoke-AlinaStage "MVP-14B9 BACKTESTING ENGINE" ".\alina_book2_backtesting_engine_mvp14b9.py"
Invoke-AlinaStage "MVP-14B10 LEARNING AND CALIBRATION" ".\alina_book2_learning_calibration_mvp14b10.py"
Invoke-AlinaStage "MVP-14B11 QUALITY SCORECARD" ".\alina_book2_quality_scorecard_mvp14b11.py"

# ---------------------------------------------------------------------
# FINAL PRODUCTION-LINE INVARIANTS
# ---------------------------------------------------------------------
$claimFiles = Get-ChildItem ".\projects\sto_let_tomu_vpered\evidence\chunk_claims_v2\primary-*.json" -ErrorAction Stop
if ($claimFiles.Count -ne 61) {
    throw "Expected 61 claim files, found $($claimFiles.Count)"
}

$required = @(
    ".\projects\sto_let_tomu_vpered\runs\mvp14b2_claim_level_canon.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b2_1_evidence_critic.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b2_2_narrative_mode_guard.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b2_3_canon_precision_gate.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b2_4_deterministic_canon_safety.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b2_5_canon_admission.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b2_6_canon_store.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b2_7_entity_registry.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b2_8_relation_event_store.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b2_9_knowledge_graph.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b3_contradiction_engine.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b4_temporal_model.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b5_state_engine.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b6_state_transition_causal.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b7_hypothesis_engine.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b8_prediction_engine.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b9_backtesting_engine.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b10_learning_calibration.json",
    ".\projects\sto_let_tomu_vpered\runs\mvp14b11_quality_scorecard.json",
    ".\projects\sto_let_tomu_vpered\reports\ALINA_QUALITY_SCORECARD.json"
)

foreach ($p in $required) {
    if (-not (Test-Path $p)) {
        throw "Missing required production artifact: $p"
    }
}

$scorecard = Get-Content ".\projects\sto_let_tomu_vpered\reports\ALINA_QUALITY_SCORECARD.json" -Raw | ConvertFrom-Json
if ($scorecard.upstream_stages_passed -ne $scorecard.upstream_stages_total) {
    throw "Quality scorecard reports incomplete upstream stages"
}

if ($scorecard.current_maturity -ne "TRUSTED_ANALYTICAL_FOUNDATION_READY") {
    throw "Unexpected maturity: $($scorecard.current_maturity)"
}

Write-Host ""
Write-Host "PASS primary_claim_files: 61" -ForegroundColor Green
Write-Host "PASS all_required_run_artifacts_exist" -ForegroundColor Green
Write-Host "PASS quality_scorecard_upstream_complete" -ForegroundColor Green
Write-Host "PASS current_maturity: $($scorecard.current_maturity)" -ForegroundColor Green
Write-Host "=== ALINA BOOK 2 FULL TRUSTED ANALYTICAL PIPELINE: PASS ===" -ForegroundColor Green
Write-Host "NOTE: publish derived artifacts after the run with .\PUBLISH_ALINA_ANALYSIS_RESULTS.ps1" -ForegroundColor Yellow
