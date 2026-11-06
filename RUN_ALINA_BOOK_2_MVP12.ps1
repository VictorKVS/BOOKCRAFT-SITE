$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA BOOK 2 COMFYUI PROVIDER MVP-12 ===" -ForegroundColor Cyan

python -m unittest .\test_comfyui_provider_mvp12.py
if ($LASTEXITCODE -ne 0) {
    throw "ComfyUI Provider MVP-12 unit tests failed"
}

try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8188/prompt" -TimeoutSec 5
    Write-Host "PASS comfyui_is_available"
}
catch {
    Write-Host "CONDITIONAL comfyui_is_not_running"
    Write-Host "Install/start ComfyUI before the real generation acceptance test."
}

Write-Host "PASS comfyui_provider_contract"
Write-Host "=== ALINA BOOK 2 COMFYUI PROVIDER MVP-12: CONTRACT PASS ===" -ForegroundColor Green
