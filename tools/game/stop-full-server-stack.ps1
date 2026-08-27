<#
.SYNOPSIS
    Stop the complete Starwing server stack.
.DESCRIPTION
    Reads PID files created by start-full-server-stack.ps1 and stops only
    those processes. Verifies ports are released.
.EXAMPLE
    .\stop-full-server-stack.ps1
#>

$ErrorActionPreference = "SilentlyContinue"
$ServerRoot  = "C:\Users\KAHO\Pictures\Starwing\server"
$PidDir      = "$ServerRoot\data"
$PidFileHTTP = "$PidDir\http_server.pid"
$PidFileProxy= "$PidDir\http_proxy.pid"
$PidFileTCP  = "$PidDir\tcp_server.pid"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  STARWING SERVER STACK STOP" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

function Stop-TrackedProcess {
    param(
        [string]$Name,
        [string]$PidFile,
        [int]$Port
    )

    if (-not (Test-Path $PidFile)) {
        Write-Host "  $Name : No PID file (not started by stack launcher)" -ForegroundColor Gray
        return
    }

    $pidStr = (Get-Content $PidFile -ErrorAction SilentlyContinue).Trim()
    if (-not $pidStr) {
        Write-Host "  $Name : Empty PID file" -ForegroundColor Gray
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        return
    }

    $procId = [int]$pidStr
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if (-not $proc) {
        Write-Host "  $Name : PID $procId not found (already stopped)" -ForegroundColor Yellow
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        return
    }

    Write-Host "  $Name : Stopping PID $procId ($($proc.Name))..." -ForegroundColor Yellow
    try {
        Stop-Process -Id $procId -Force -ErrorAction Stop
        Write-Host "  $Name : Stopped" -ForegroundColor Green
    } catch {
        Write-Host "  $Name : Failed to stop - $($_.Exception.Message)" -ForegroundColor Red
    }
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

# ── Stop tracked processes ───────────────────────────────
Write-Host "`nStopping tracked processes..." -ForegroundColor Yellow

Stop-TrackedProcess -Name "HTTP Server :4001" -PidFile $PidFileHTTP -Port 4001
Stop-TrackedProcess -Name "HTTP Proxy  :80"   -PidFile $PidFileProxy -Port 80
Stop-TrackedProcess -Name "TCP Server  :6666" -PidFile $PidFileTCP -Port 6666

# ── Kill any remaining python on our ports ────────────────
Write-Host "`nChecking for remaining processes on ports..." -ForegroundColor Yellow
foreach ($port in @(80, 4001, 6666)) {
    $remaining = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    foreach ($conn in $remaining) {
        $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "  Killing $($proc.Name) PID=$($proc.Id) on port $port" -ForegroundColor Yellow
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
    }
}

# ── Verify ports are released ────────────────────────────
Write-Host "`nVerifying ports released..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

$allClear = $true
foreach ($port in @(80, 4001, 6666)) {
    $remaining = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($remaining) {
        Write-Host "  Port $port : STILL IN USE" -ForegroundColor Red
        $allClear = $false
    } else {
        Write-Host "  Port $port : Released" -ForegroundColor Green
    }
}

# ── Final status ─────────────────────────────────────────
Write-Host "`n============================================" -ForegroundColor Cyan
if ($allClear) {
    Write-Host "  ALL SERVERS STOPPED AND PORTS RELEASED" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Some ports still in use" -ForegroundColor Yellow
}
Write-Host "============================================" -ForegroundColor Cyan
