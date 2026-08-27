<#
.SYNOPSIS
    Safe launch wrapper for Starwing Paradox game.
.DESCRIPTION
    Starts the backend server and launches the game with safety checks.
.PARAMETER SkipServer
    Skip starting the backend server.
.PARAMETER Windowed
    Force windowed mode.
.PARAMETER Resolution
    Set resolution (e.g., "1280x720").
.EXAMPLE
    .\start-game.ps1
    .\start-game.ps1 -SkipServer -Windowed
#>
param(
    [switch]$SkipServer,
    [switch]$Windowed,
    [string]$Resolution = "1920x1080"
)

$ErrorActionPreference = "Stop"
$GameRoot = "X:\StarwingParadox"
$ServerRoot = "C:\Users\KAHO\Pictures\Starwing\server"
$GameExe = "$GameRoot\WindowsNoEditor\AcrGame.exe"
$ShippingExe = "$GameRoot\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe"

Write-Host "=== Starwing Paradox Safe Launch ===" -ForegroundColor Cyan

# Step 1: Verify game files
Write-Host "`n[1/5] Verifying game files..." -ForegroundColor Yellow
if (-not (Test-Path $GameExe)) {
    Write-Host "ERROR: AcrGame.exe not found at $GameExe" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $ShippingExe)) {
    Write-Host "ERROR: AcrGame-Win64-Shipping.exe not found" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: AcrGame.exe found" -ForegroundColor Green
Write-Host "  OK: AcrGame-Win64-Shipping.exe found" -ForegroundColor Green

# Step 2: Verify network ports
Write-Host "`n[2/5] Checking network ports..." -ForegroundColor Yellow
$port4001 = Get-NetTCPConnection -LocalPort 4001 -ErrorAction SilentlyContinue
$port6666 = Get-NetTCPConnection -LocalPort 6666 -ErrorAction SilentlyContinue
if ($port4001) {
    Write-Host "  WARNING: Port 4001 already in use" -ForegroundColor Yellow
} else {
    Write-Host "  OK: Port 4001 available" -ForegroundColor Green
}
if ($port6666) {
    Write-Host "  WARNING: Port 6666 already in use" -ForegroundColor Yellow
} else {
    Write-Host "  OK: Port 6666 available" -ForegroundColor Green
}

# Step 3: Start backend server (optional)
if (-not $SkipServer) {
    Write-Host "`n[3/5] Starting backend server..." -ForegroundColor Yellow
    $serverProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory $ServerRoot -PassThru -NoNewWindow
    Start-Sleep -Seconds 3
    Write-Host "  OK: Server started (PID: $($serverProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "`n[3/5] Skipping backend server (--SkipServer)" -ForegroundColor Yellow
    $serverProcess = $null
}

# Step 4: Launch game
Write-Host "`n[4/5] Launching game..." -ForegroundColor Yellow
$launchArgs = @()
if ($Windowed) {
    $launchArgs += "-windowed"
}
if ($Resolution -ne "1920x1080") {
    $resParts = $Resolution.Split("x")
    $launchArgs += "-resx=$($resParts[0])"
    $launchArgs += "-resy=$($resParts[1])"
}
$launchArgs += "-log"

Write-Host "  Command: $GameExe $($launchArgs -join ' ')" -ForegroundColor Gray
$gameProcess = Start-Process -FilePath $GameExe -ArgumentList $launchArgs -PassThru
Write-Host "  OK: Game launched (PID: $($gameProcess.Id))" -ForegroundColor Green

# Step 5: Monitor
Write-Host "`n[5/5] Monitoring (Ctrl+C to stop)..." -ForegroundColor Yellow
Write-Host "  Game PID: $($gameProcess.Id)" -ForegroundColor Gray
if ($serverProcess) {
    Write-Host "  Server PID: $($serverProcess.Id)" -ForegroundColor Gray
}

try {
    while (-not $gameProcess.HasExited) {
        Start-Sleep -Seconds 5
        Write-Host "  Game running... (PID: $($gameProcess.Id))" -ForegroundColor Gray
    }
    Write-Host "`nGame exited with code: $($gameProcess.ExitCode)" -ForegroundColor Yellow
} finally {
    if ($serverProcess -and -not $serverProcess.HasExited) {
        Write-Host "Stopping server..." -ForegroundColor Yellow
        Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "Server stopped" -ForegroundColor Green
    }
}
