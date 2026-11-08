$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA LOCAL FACTORY ===" -ForegroundColor Cyan

$portFrontend = 5180
$portBackend = 8191
$portOllama = 11434

function Stop-Port([int]$port) {
    $pids = @(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique)
    foreach ($p in $pids) {
        if ($p) {
            Write-Host "Stopping PID=$p on port $port"
            Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        }
    }
}

Stop-Port $portFrontend
Stop-Port $portBackend

# Local LLM for DEEP ANALYSIS
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
$ollamaListening = Get-NetTCPConnection -LocalPort $portOllama -State Listen -ErrorAction SilentlyContinue
if ($ollamaListening) {
    Write-Host "Local LLM: Ollama is already listening on http://127.0.0.1:$portOllama" -ForegroundColor Green
} elseif ($ollamaCmd) {
    Write-Host "Local LLM: starting Ollama..." -ForegroundColor Cyan
    Start-Process -FilePath $ollamaCmd.Source -ArgumentList "serve" -WindowStyle Hidden | Out-Null
    Start-Sleep -Seconds 2
    $ollamaListening = Get-NetTCPConnection -LocalPort $portOllama -State Listen -ErrorAction SilentlyContinue
    if ($ollamaListening) {
        Write-Host "Local LLM: Ollama started." -ForegroundColor Green
    } else {
        Write-Host "Local LLM: Ollama command found but server did not start." -ForegroundColor Yellow
    }
} else {
    Write-Host "Local LLM: Ollama not found. Foundation ingest will work; DEEP ANALYSIS requires a local LLM." -ForegroundColor Yellow
    Write-Host "You can also set ALINA_LLM_BASE_URL and ALINA_LLM_MODEL for a local OpenAI-compatible server." -ForegroundColor DarkYellow
}

if ($ollamaCmd -or $ollamaListening) {
    try {
        $models = & ollama list 2>$null
        Write-Host "Local models:" -ForegroundColor Cyan
        $models | Select-Object -First 8 | ForEach-Object { Write-Host "  $_" }
    } catch {}
}


if (-not (Test-Path ".venv-alina")) {
    Write-Host "Creating Python venv..."
    python -m venv .venv-alina
}

$python = Join-Path $PSScriptRoot ".venv-alina\Scripts\python.exe"
$pip = Join-Path $PSScriptRoot ".venv-alina\Scripts\pip.exe"

Write-Host "Installing/checking backend dependencies..."
& $pip install -r requirements-alina.txt

Write-Host "Starting ALINA backend on http://127.0.0.1:$portBackend ..."
$backend = Start-Process -FilePath $python -ArgumentList "-m","uvicorn","backend.alina_api:app","--host","127.0.0.1","--port","$portBackend","--reload" -WorkingDirectory $PSScriptRoot -PassThru

Start-Sleep -Seconds 2

Write-Host "Starting BOOKCRAFT frontend on http://127.0.0.1:$portFrontend ..."
npm run dev

if ($backend -and -not $backend.HasExited) {
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
}
