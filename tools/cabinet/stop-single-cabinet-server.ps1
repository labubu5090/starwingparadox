<#
.SYNOPSIS
    Stop the Starwing Paradox single-cabinet server.
.DESCRIPTION
    Gracefully shuts down the server process using the stored PID.
    Falls back to port-based detection if PID file is missing.
.PARAMETER Host
    Server host for health verification (default: 127.0.0.1)
.PARAMETER Port
    Server port to stop (default: 4001)
#>
param(
    [string]$Host = "127.0.0.1",
    [string]$Port = "4001"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RuntimeDir = Join-Path $ProjectRoot "runtime"
$PidFile = Join-Path $RuntimeDir "starwing-single-cabinet.pid"

Write-Host "Stopping Starwing Paradox server..." -ForegroundColor Cyan

$stopped = $false

# Try PID-based stop first
if (Test-Path $PidFile) {
    $pid = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($pid) {
        $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "  Stopping process PID: $pid" -ForegroundColor Gray
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            $proc.WaitForExit(5000)
            $stopped = $true
        }
    }
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

# Fallback: kill by port
if (-not $stopped) {
    $conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
            Where-Object { $_.State -eq "Listen" } |
            Select-Object -First 1
    if ($conn) {
        Write-Host "  Stopping process on port $Port (PID: $($conn.OwningProcess))" -ForegroundColor Gray
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        $stopped = $true
    }
}

if ($stopped) {
    # Verify shutdown
    Start-Sleep -Seconds 1
    $check = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
             Where-Object { $_.State -eq "Listen" }
    if ($check) {
        Write-Warning "Process may still be running on port $Port"
    } else {
        Write-Host "Server stopped successfully" -ForegroundColor Green
    }
} else {
    Write-Host "No running server found" -ForegroundColor Yellow
}