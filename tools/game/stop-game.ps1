<#
.SYNOPSIS
    Stop game and server processes.
.DESCRIPTION
    Gracefully stops game and server processes.
.EXAMPLE
    .\stop-game.ps1
#>

$ErrorActionPreference = "SilentlyContinue"

Write-Host "=== Stopping Starwing Paradox ===" -ForegroundColor Cyan

# Stop game processes
$gameProcs = Get-Process -Name "AcrGame*" -ErrorAction SilentlyContinue
if ($gameProcs) {
    foreach ($proc in $gameProcs) {
        Write-Host "Stopping game process: $($proc.Name) (PID: $($proc.Id))" -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force
    }
    Write-Host "Game processes stopped" -ForegroundColor Green
} else {
    Write-Host "No game processes found" -ForegroundColor Gray
}

# Stop server
$serverProcs = Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn*" }
if ($serverProcs) {
    foreach ($proc in $serverProcs) {
        Write-Host "Stopping server process: $($proc.Name) (PID: $($proc.Id))" -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force
    }
    Write-Host "Server processes stopped" -ForegroundColor Green
} else {
    Write-Host "No server processes found" -ForegroundColor Gray
}

Write-Host "`nDone." -ForegroundColor Green
