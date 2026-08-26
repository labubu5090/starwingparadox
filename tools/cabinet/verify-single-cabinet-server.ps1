<#
.SYNOPSIS
    Verify the Starwing Paradox single-cabinet server is running correctly.
.DESCRIPTION
    Checks HTTP health endpoint, readiness endpoint, and TCP port availability.
    Exits with non-zero code on failure.
.PARAMETER Host
    Server host (default: 127.0.0.1)
.PARAMETER Port
    HTTP port (default: 4001)
.PARAMETER TCPPort
    TCP protobuf port (default: 6666)
#>
param(
    [string]$Host = "127.0.0.1",
    [string]$Port = "4001",
    [string]$TCPPort = "6666"
)

$ErrorActionPreference = "Stop"

Write-Host "Verifying single-cabinet server..." -ForegroundColor Cyan

$allPassed = $true

# Test 1: HTTP Health endpoint
Write-Host "`n[1/4] Health endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://${Host}:${Port}/health" -Method Get -TimeoutSec 5
    if ($health.status -eq "ok") {
        Write-Host "  [OK] Health: $($health.status)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] Health returned: $($health.status)" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    Write-Host "  [FAIL] Health endpoint unreachable: $_" -ForegroundColor Red
    $allPassed = $false
}

# Test 2: Readiness endpoint
Write-Host "`n[2/4] Readiness endpoint..." -ForegroundColor Yellow
try {
    $ready = Invoke-RestMethod -Uri "http://${Host}:${Port}/ready" -Method Get -TimeoutSec 5
    if ($ready.status -eq "ready") {
        Write-Host "  [OK] Ready: $($ready.status), DB: $($ready.database)" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] Readiness: $($ready.status), DB: $($ready.database)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [FAIL] Readiness endpoint unreachable: $_" -ForegroundColor Red
    $allPassed = $false
}

# Test 3: TCP port listening
Write-Host "`n[3/4] TCP port $TCPPort..." -ForegroundColor Yellow
$tcpConn = Get-NetTCPConnection -LocalPort $TCPPort -ErrorAction SilentlyContinue |
           Where-Object { $_.State -eq "Listen" } |
           Select-Object -First 1
if ($tcpConn) {
    Write-Host "  [OK] TCP listening on port $TCPPort (PID: $($tcpConn.OwningProcess))" -ForegroundColor Green
} else {
    Write-Host "  [WARN] TCP port $TCPPort not listening (TCP may be disabled)" -ForegroundColor Yellow
}

# Test 4: Process check
Write-Host "`n[4/4] Process check..." -ForegroundColor Yellow
$RuntimeDir = Join-Path (Resolve-Path (Join-Path $PSScriptRoot "..\..")) "runtime"
$PidFile = Join-Path $RuntimeDir "starwing-single-cabinet.pid"
if (Test-Path $PidFile) {
    $pid = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($pid) {
        $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "  [OK] Server process running (PID: $pid)" -ForegroundColor Green
        } else {
            Write-Host "  [FAIL] PID file exists but process $pid not found" -ForegroundColor Red
            $allPassed = $false
        }
    }
} else {
    Write-Host "  [WARN] No PID file found" -ForegroundColor Yellow
}

# Summary
Write-Host "`n" -NoNewline
if ($allPassed) {
    Write-Host "Verification PASSED" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Verification FAILED" -ForegroundColor Red
    exit 1
}