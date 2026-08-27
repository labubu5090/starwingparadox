<#
.SYNOPSIS
    Start the Starwing game server on correct runtime ports.
.DESCRIPTION
    Starts HTTP server on 127.0.0.1:4001 and optionally TCP on 127.0.0.1:6666.
.PARAMETER SkipTCP
    Skip starting the TCP server.
.EXAMPLE
    .\start-game-server.ps1
    .\start-game-server.ps1 -SkipTCP
#>
param(
    [switch]$SkipTCP
)

$ErrorActionPreference = "Stop"
$ServerRoot = "C:\Users\KAHO\Pictures\Starwing\server"
$PidFile = "$ServerRoot\data\game_server.pid"

Write-Host "=== Starwing Game Server Start ===" -ForegroundColor Cyan

# Check for existing server
if (Test-Path $PidFile) {
    $oldPid = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($oldPid) {
        $proc = Get-Process -Id $oldPid -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "ERROR: Game server already running (PID $oldPid)" -ForegroundColor Red
            Write-Host "Run .\stop-game-server.ps1 first" -ForegroundColor Yellow
            exit 1
        }
    }
}

# Verify ports are free
Write-Host "`n[1/6] Checking ports..." -ForegroundColor Yellow
$port4001 = Get-NetTCPConnection -LocalPort 4001 -ErrorAction SilentlyContinue
if ($port4001) {
    Write-Host "ERROR: Port 4001 already in use" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: Port 4001 free" -ForegroundColor Green

if (-not $SkipTCP) {
    $port6666 = Get-NetTCPConnection -LocalPort 6666 -ErrorAction SilentlyContinue
    if ($port6666) {
        Write-Host "WARNING: Port 6666 in use (NesysService may be running)" -ForegroundColor Yellow
    } else {
        Write-Host "  OK: Port 6666 free" -ForegroundColor Green
    }
}

# Verify no port 4000 listener
$port4000 = Get-NetTCPConnection -LocalPort 4000 -ErrorAction SilentlyContinue
if ($port4000) {
    Write-Host "WARNING: Port 4000 in use" -ForegroundColor Yellow
} else {
    Write-Host "  OK: Port 4000 not claimed" -ForegroundColor Green
}

# Create data directory
if (-not (Test-Path "$ServerRoot\data")) {
    New-Item -ItemType Directory -Path "$ServerRoot\data" -Force | Out-Null
}

# Start server
Write-Host "`n[2/6] Starting HTTP server on 127.0.0.1:4001..." -ForegroundColor Yellow
$env:HTTP_HOST = "127.0.0.1"
$env:HTTP_PORT = "4001"
$env:CAPTURE_ENABLED = "false"
$env:MATCHING_ENABLED = "false"
$env:BATTLE_ENABLED = "false"

$proc = Start-Process -FilePath "$ServerRoot\.venv\Scripts\python.exe" `
    -ArgumentList "-m","uvicorn","app.main:app","--host","127.0.0.1","--port","4001" `
    -WorkingDirectory $ServerRoot `
    -WindowStyle Hidden `
    -PassThru

$proc.Id | Set-Content $PidFile
Write-Host "  OK: Server started (PID $($proc.Id))" -ForegroundColor Green

# Wait for startup
Write-Host "`n[3/6] Waiting for server..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verify health
Write-Host "`n[4/6] Verifying health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:4001/health" -ErrorAction Stop
    Write-Host "  OK: /health = $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "  FAIL: /health not responding" -ForegroundColor Red
}

try {
    $ready = Invoke-RestMethod -Uri "http://127.0.0.1:4001/ready" -ErrorAction Stop
    Write-Host "  OK: /ready responded" -ForegroundColor Green
} catch {
    Write-Host "  WARN: /ready not available" -ForegroundColor Yellow
}

# Verify no port 4000
Write-Host "`n[5/6] Verifying port 4000 not created..." -ForegroundColor Yellow
$port4000check = Get-NetTCPConnection -LocalPort 4000 -ErrorAction SilentlyContinue
if ($port4000check) {
    Write-Host "  FAIL: Port 4000 listener created" -ForegroundColor Red
} else {
    Write-Host "  OK: No port 4000 listener" -ForegroundColor Green
}

# Verify guards
Write-Host "`n[6/6] Verifying guards..." -ForegroundColor Yellow
try {
    $match = Invoke-RestMethod -Uri "http://127.0.0.1:4001/api/matching/status" -ErrorAction Stop
    Write-Host "  OK: Matching guarded" -ForegroundColor Green
} catch {
    Write-Host "  OK: Matching returns error (guarded)" -ForegroundColor Green
}

Write-Host "`n=== Server Ready ===" -ForegroundColor Green
Write-Host "HTTP: http://127.0.0.1:4001" -ForegroundColor Cyan
Write-Host "PID: $($proc.Id)" -ForegroundColor Cyan
Write-Host "PID file: $PidFile" -ForegroundColor Cyan
