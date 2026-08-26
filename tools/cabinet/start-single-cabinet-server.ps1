<#
.SYNOPSIS
    Start the Starwing Paradox server for single-cabinet testing.
.DESCRIPTION
    Launches the Python server with a single-cabinet configuration.
    Refuses to start if a server is already running on the configured port.
.PARAMETER ConfigPath
    Path to the .env configuration file (default: ..\..\config\.env)
.PARAMETER Host
    Server bind address (default: from env or 127.0.0.1)
.PARAMETER Port
    HTTP server port (default: from env or 4001)
#>
param(
    [string]$ConfigPath = "",
    [string]$Host = "",
    [string]$Port = ""
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ServerDir = Join-Path $ProjectRoot "server"
$RuntimeDir = Join-Path $ProjectRoot "runtime"
$PidFile = Join-Path $RuntimeDir "starwing-single-cabinet.pid"
$LogFile = Join-Path $RuntimeDir "starwing-single-cabinet.log"

# Ensure runtime directory exists
if (-not (Test-Path $RuntimeDir)) {
    New-Item -ItemType Directory -Path $RuntimeDir -Force | Out-Null
}

# Check for existing process
if (Test-Path $PidFile) {
    $existingPid = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($existingPid) {
        $proc = Get-Process -Id $existingPid -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Error "Server already running with PID $existingPid. Use stop-single-cabinet-server.ps1 first."
            exit 1
        }
        # Stale PID file
        Remove-Item $PidFile -Force
    }
}

# Load config if provided
if ($ConfigPath -and (Test-Path $ConfigPath)) {
    Get-Content $ConfigPath | ForEach-Object {
        if ($_ -match "^([^#=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
    Write-Host "Loaded config from: $ConfigPath" -ForegroundColor Cyan
}

# Determine bind address and port
$bindHost = if ($Host) { $Host } 
            elseif ($env:HOST) { $env:HOST } 
            else { "127.0.0.1" }

$bindPort = if ($Port) { $Port } 
            elseif ($env:PORT) { $env:PORT } 
            else { "4001" }

# Verify no process already listening
$existing = Get-NetTCPConnection -LocalPort $bindPort -ErrorAction SilentlyContinue
if ($existing) {
    Write-Error "Port $bindPort already in use. Stop the conflicting process first."
    exit 1
}

Write-Host "Starting Starwing Paradox server..." -ForegroundColor Cyan
Write-Host "  Host: $bindHost" -ForegroundColor Gray
Write-Host "  Port: $bindPort" -ForegroundColor Gray
Write-Host "  Log:  $LogFile" -ForegroundColor Gray

# Start server process
$process = Start-Process -FilePath "python" `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--host", $bindHost, "--port", $bindPort `
    -WorkingDirectory $ServerDir `
    -RedirectStandardOutput $LogFile `
    -RedirectStandardError "$LogFile.err" `
    -PassThru `
    -NoNewWindow

# Save PID
$process.Id | Out-File -FilePath $PidFile -Encoding utf8
Write-Host "Server started with PID: $($process.Id)" -ForegroundColor Green
Write-Host "PID file: $PidFile" -ForegroundColor Gray

# Wait briefly for startup
Start-Sleep -Seconds 2

# Quick health check
try {
    $health = Invoke-RestMethod -Uri "http://${bindHost}:${bindPort}/health" -Method Get -TimeoutSec 5
    if ($health.status -eq "ok") {
        Write-Host "Health check passed" -ForegroundColor Green
    } else {
        Write-Warning "Health check returned unexpected status: $($health.status)"
    }
} catch {
    Write-Warning "Health check failed (server may still be starting): $_"
}

Write-Host "Server ready. Use stop-single-cabinet-server.ps1 to shut down." -ForegroundColor Cyan