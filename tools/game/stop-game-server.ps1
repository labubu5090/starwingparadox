<#
.SYNOPSIS
    Stop the Starwing game server.
.EXAMPLE
    .\stop-game-server.ps1
#>

$ErrorActionPreference = "SilentlyContinue"
$ServerRoot = "C:\Users\KAHO\Pictures\Starwing\server"
$PidFile = "$ServerRoot\data\game_server.pid"

Write-Host "=== Starwing Game Server Stop ===" -ForegroundColor Cyan

if (Test-Path $PidFile) {
    $pid = Get-Content $PidFile
    $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Host "Stopping server (PID $pid)..." -ForegroundColor Yellow
        Stop-Process -Id $pid -Force
        Write-Host "Stopped" -ForegroundColor Green
    } else {
        Write-Host "Process $pid not found (already stopped)" -ForegroundColor Yellow
    }
    Remove-Item $PidFile -Force
} else {
    Write-Host "No PID file found" -ForegroundColor Yellow
}

# Also kill any lingering python on port 4001
$conns = Get-NetTCPConnection -LocalPort 4001 -ErrorAction SilentlyContinue
foreach ($c in $conns) {
    $proc = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue
    if ($proc -and $proc.Name -eq "python") {
        Write-Host "Killing lingering python on port 4001 (PID $($c.OwningProcess))" -ForegroundColor Yellow
        Stop-Process -Id $c.OwningProcess -Force
    }
}

Write-Host "Done" -ForegroundColor Green
