$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== ALINA LOCAL FACTORY ===" -ForegroundColor Cyan

$portFrontend = 5180
$portBackend = 8191
$portOllama = 11434

function Stop-Port([int]$port) {
    $attempted = @{}
    for ($attempt = 1; $attempt -le 8; $attempt++) {
        $connections = @(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
        if (-not $connections -or $connections.Count -eq 0) {
            Write-Host "Port $port is free." -ForegroundColor DarkGreen
            return $true
        }

        $ownerPids = @($connections | Select-Object -ExpandProperty OwningProcess -Unique)
        foreach ($ownerPid in $ownerPids) {
            if ($ownerPid -and -not $attempted.ContainsKey([string]$ownerPid)) {
                $attempted[[string]$ownerPid] = $true
                try {
                    $proc = Get-CimInstance Win32_Process -Filter "ProcessId=$ownerPid" -ErrorAction SilentlyContinue
                    $cmd = if ($proc) { $proc.CommandLine } else { "" }
                    Write-Host "Stopping PID=$ownerPid on port $port $cmd" -ForegroundColor DarkYellow
                    Stop-Process -Id $ownerPid -Force -ErrorAction SilentlyContinue
                } catch {}
            }
        }

        Start-Sleep -Milliseconds 700
    }

    $remaining = @(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
    if ($remaining.Count -gt 0) {
        Write-Host "Port $port is still occupied after cleanup:" -ForegroundColor Red
        foreach ($conn in $remaining) {
            $ownerPid = $conn.OwningProcess
            $proc = Get-CimInstance Win32_Process -Filter "ProcessId=$ownerPid" -ErrorAction SilentlyContinue
            Write-Host "  PID=$ownerPid  $($proc.Name)  $($proc.CommandLine)" -ForegroundColor Yellow
        }
        return $false
    }
    return $true
}

function Stop-OldAlinaBackend {
    $old = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -and $_.CommandLine -match "backend\.alina_api:app"
    }
    foreach ($proc in $old) {
        Write-Host "Stopping old ALINA backend PID=$($proc.ProcessId)" -ForegroundColor DarkYellow
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Milliseconds 700
}

Stop-Port $portFrontend | Out-Null
$backendPortFree = Stop-Port $portBackend
Stop-OldAlinaBackend
$backendPortFree = Stop-Port $portBackend

if (-not $backendPortFree) {
    throw "Port $portBackend could not be released. ALINA backend cannot start safely."
}

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

# Optional llama-cpp-python support for direct GGUF mode.
# IMPORTANT: this check must never stop ALINA when Ollama is already available.
if (-not $ollamaListening) {
    $oldErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    & $python -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('llama_cpp') else 1)" *> $null
    $venvHasLlama = ($LASTEXITCODE -eq 0)

    if (-not $venvHasLlama) {
        & python -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('llama_cpp') else 1)" *> $null
        $systemHasLlama = ($LASTEXITCODE -eq 0)

        if ($systemHasLlama) {
            $cfg = Join-Path $PSScriptRoot ".venv-alina\pyvenv.cfg"
            if (Test-Path $cfg) {
                (Get-Content $cfg) -replace "include-system-site-packages = false","include-system-site-packages = true" | Set-Content $cfg -Encoding UTF8
                Write-Host "Local LLM engine: linked system llama-cpp-python into .venv-alina." -ForegroundColor Green
            }
        } else {
            Write-Host "Local LLM engine: llama-cpp-python not found. Direct GGUF mode unavailable." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Local LLM engine: llama-cpp-python is available in .venv-alina." -ForegroundColor Green
    }

    $ErrorActionPreference = $oldErrorActionPreference
} else {
    Write-Host "Local LLM engine: using Ollama; llama-cpp-python check skipped." -ForegroundColor Green
}

$backendPortFree = Stop-Port $portBackend
if (-not $backendPortFree) {
    throw "Port $portBackend is still occupied immediately before backend start."
}

Write-Host "Starting ALINA backend on http://127.0.0.1:$portBackend ..."
$backendLog = Join-Path $PSScriptRoot ".alina-private\backend.log"
$backendErr = Join-Path $PSScriptRoot ".alina-private\backend-error.log"
New-Item -ItemType Directory -Force -Path (Split-Path $backendLog) | Out-Null
$backend = Start-Process -FilePath $python -ArgumentList "-m","uvicorn","backend.alina_api:app","--host","127.0.0.1","--port","$portBackend" -WorkingDirectory $PSScriptRoot -RedirectStandardOutput $backendLog -RedirectStandardError $backendErr -PassThru

# Wait for exact backend revision and verify critical routes.
$backendReady = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:$portBackend/api/health" -Method Get -TimeoutSec 2
        $openapi = Invoke-RestMethod -Uri "http://127.0.0.1:$portBackend/openapi.json" -Method Get -TimeoutSec 2
        $hasProjectsPost = $false
        if ($openapi.paths.PSObject.Properties.Name -contains "/api/projects") {
            $projectPath = $openapi.paths."/api/projects"
            $hasProjectsPost = $null -ne $projectPath.post
        }
        if ($health.status -eq "ok" -and $hasProjectsPost) {
            $backendReady = $true
            Write-Host "Backend self-test: PASS (/api/projects POST available)" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $backendReady) {
    Write-Host "Backend self-test: FAIL. Frontend will not start." -ForegroundColor Red
    if (Test-Path $backendErr) {
        Write-Host "--- backend-error.log ---" -ForegroundColor Yellow
        Get-Content $backendErr -Tail 40
    }
    if ($backend -and -not $backend.HasExited) {
        Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    }
    throw "ALINA backend route /api/projects POST is unavailable"
}

Write-Host "Starting BOOKCRAFT frontend on http://127.0.0.1:$portFrontend ..."
npm run dev

if ($backend -and -not $backend.HasExited) {
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
}
