$ErrorActionPreference = "Continue"

Write-Host "=== ALINA BOOK 2 / COMFYUI ENVIRONMENT CHECK ===" -ForegroundColor Cyan

$pass = $true

Write-Host ""
Write-Host "[1] NVIDIA"
try {
    $gpu = & nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>$null
    if ($LASTEXITCODE -eq 0 -and $gpu) {
        Write-Host "PASS NVIDIA: $gpu" -ForegroundColor Green
    }
    else {
        Write-Host "FAIL NVIDIA driver/GPU not visible through nvidia-smi" -ForegroundColor Red
        $pass = $false
    }
}
catch {
    Write-Host "FAIL nvidia-smi not found" -ForegroundColor Red
    $pass = $false
}

Write-Host ""
Write-Host "[2] ComfyUI candidate locations"

$candidates = @(
    "G:\1\ComfyUI_windows_portable",
    "G:\1\ComfyUI",
    "$env:USERPROFILE\ComfyUI",
    "$env:LOCALAPPDATA\Programs\ComfyUI"
)

$found = @()
foreach ($path in $candidates) {
    if (Test-Path $path) {
        Write-Host "FOUND $path" -ForegroundColor Green
        $found += $path
    }
}

if ($found.Count -eq 0) {
    Write-Host "CONDITIONAL ComfyUI files not found in common locations" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3] Local API :8188"
try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8188/prompt" -TimeoutSec 5
    Write-Host "PASS ComfyUI API reachable: HTTP $($response.StatusCode)" -ForegroundColor Green
}
catch {
    Write-Host "CONDITIONAL ComfyUI API is not running at http://127.0.0.1:8188" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4] Model folders"
foreach ($root in $found) {
    $possible = @(
        (Join-Path $root "ComfyUI\models\checkpoints"),
        (Join-Path $root "models\checkpoints")
    )
    foreach ($p in $possible) {
        if (Test-Path $p) {
            $models = Get-ChildItem $p -File -ErrorAction SilentlyContinue |
                Where-Object { $_.Extension -in @(".safetensors", ".ckpt") }
            Write-Host "MODEL_DIR $p"
            Write-Host "CHECKPOINT_COUNT $($models.Count)"
            foreach ($m in $models) {
                Write-Host "  $($m.Name)"
            }
        }
    }
}

Write-Host ""
if ($pass) {
    Write-Host "=== BASE ENVIRONMENT: PASS ===" -ForegroundColor Green
}
else {
    Write-Host "=== BASE ENVIRONMENT: FAIL ===" -ForegroundColor Red
    exit 1
}
