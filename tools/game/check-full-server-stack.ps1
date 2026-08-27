<#
.SYNOPSIS
    Check the status of the complete Starwing server stack.
.DESCRIPTION
    Reports on ports 80, 4001, 6666 and tests health/matching endpoints.
.EXAMPLE
    .\check-full-server-stack.ps1
#>

$ErrorActionPreference = "SilentlyContinue"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  STARWING SERVER STACK STATUS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ── Port status ──────────────────────────────────────────
Write-Host "`nPORT STATUS:" -ForegroundColor Yellow

foreach ($portInfo in @(
    @{ Port=80;   Name="HTTP Proxy" },
    @{ Port=4001; Name="HTTP Server" },
    @{ Port=6666; Name="TCP Server" }
)) {
    $port = $portInfo.Port
    $name = $portInfo.Name
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conns) {
        $pid = $conns[0].OwningProcess
        $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
        $procName = if ($proc) { $proc.ProcessName } else { "unknown" }
        $procPath = if ($proc -and $proc.Path) { $proc.Path } else { "N/A" }
        Write-Host "  $port ($name) : LISTENING" -ForegroundColor Green
        Write-Host "    PID: $pid  Process: $procName" -ForegroundColor Gray
        Write-Host "    Path: $procPath" -ForegroundColor Gray
    } else {
        Write-Host "  $port ($name) : NOT LISTENING" -ForegroundColor Red
    }
}

# ── HTTP Server health ──────────────────────────────────
Write-Host "`nHTTP ENDPOINTS:" -ForegroundColor Yellow

# Test /health
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:4001/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  GET http://127.0.0.1:4001/health" -ForegroundColor Gray
    Write-Host "    Status: $($resp.StatusCode)" -ForegroundColor Green
    Write-Host "    Body:   $($resp.Content)" -ForegroundColor Gray
} catch {
    Write-Host "  GET http://127.0.0.1:4001/health : FAILED" -ForegroundColor Red
    Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Gray
}

# Test /ready
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:4001/ready" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  GET http://127.0.0.1:4001/ready" -ForegroundColor Gray
    Write-Host "    Status: $($resp.StatusCode)" -ForegroundColor Green
    Write-Host "    Body:   $($resp.Content)" -ForegroundColor Gray
} catch {
    Write-Host "  GET http://127.0.0.1:4001/ready : FAILED" -ForegroundColor Red
}

# ── Proxy test (game's actual URL) ──────────────────────
Write-Host "`nPROXY ENDPOINTS (game URL):" -ForegroundColor Yellow

# The game hits dev.starwing.jp/mock/matching/server via POST
try {
    $resp = Invoke-WebRequest -Uri "http://dev.starwing.jp/mock/matching/server" `
        -Method POST `
        -Headers @{ "Content-Type" = "application/octet-stream" } `
        -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  POST http://dev.starwing.jp/mock/matching/server" -ForegroundColor Gray
    Write-Host "    Status: $($resp.StatusCode)" -ForegroundColor Green
    Write-Host "    Body:   $($resp.Content)" -ForegroundColor Gray
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "  POST http://dev.starwing.jp/mock/matching/server" -ForegroundColor Gray
    Write-Host "    Status: $statusCode" -ForegroundColor $(if ($statusCode -eq 501) {'Yellow'} else {'Red'})
    if ($statusCode -eq 501) {
        Write-Host "    (501 = matching guarded, expected)" -ForegroundColor Gray
    } else {
        Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Gray
    }
}

# Also test GET for comparison
try {
    $resp = Invoke-WebRequest -Uri "http://dev.starwing.jp/mock/matching/server" `
        -Method GET `
        -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  GET  http://dev.starwing.jp/mock/matching/server" -ForegroundColor Gray
    Write-Host "    Status: $($resp.StatusCode)" -ForegroundColor Green
    Write-Host "    Body:   $($resp.Content)" -ForegroundColor Gray
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "  GET  http://dev.starwing.jp/mock/matching/server : $statusCode" -ForegroundColor Gray
}

# ── Direct backend test ──────────────────────────────────
Write-Host "`nDIRECT BACKEND (bypass proxy):" -ForegroundColor Yellow
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:4001/matching/server" `
        -Method POST `
        -Headers @{ "Content-Type" = "application/octet-stream" } `
        -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  POST http://127.0.0.1:4001/matching/server" -ForegroundColor Gray
    Write-Host "    Status: $($resp.StatusCode)" -ForegroundColor Green
    Write-Host "    Body:   $($resp.Content)" -ForegroundColor Gray
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "  POST http://127.0.0.1:4001/matching/server : $statusCode" -ForegroundColor Gray
}

# ── PID files ────────────────────────────────────────────
Write-Host "`nPID FILES:" -ForegroundColor Yellow
$PidDir = "C:\Users\KAHO\Pictures\Starwing\server\data"
foreach ($pf in @("http_server.pid", "http_proxy.pid", "tcp_server.pid")) {
    $path = Join-Path $PidDir $pf
    if (Test-Path $path) {
        $pid = (Get-Content $path).Trim()
        $proc = Get-Process -Id ([int]$pid) -ErrorAction SilentlyContinue
        $status = if ($proc) { "RUNNING ($($proc.ProcessName))" } else { "DEAD" }
        Write-Host "  $pf : PID $pid - $status" -ForegroundColor $(if ($proc) {'Green'} else {'Red'})
    } else {
        Write-Host "  $pf : NOT FOUND" -ForegroundColor Gray
    }
}

# ── Hosts file check ────────────────────────────────────
Write-Host "`nHOSTS FILE:" -ForegroundColor Yellow
$hostsContent = Get-Content "C:\Windows\System32\drivers\etc\hosts" -ErrorAction SilentlyContinue
$devEntry = $hostsContent | Where-Object { $_ -match "dev\.starwing\.jp" }
if ($devEntry) {
    Write-Host "  dev.starwing.jp entry found: $devEntry" -ForegroundColor Green
} else {
    Write-Host "  dev.starwing.jp entry NOT FOUND" -ForegroundColor Red
    Write-Host "  Proxy will not work without this entry." -ForegroundColor Yellow
}

# ── Game processes ───────────────────────────────────────
Write-Host "`nGAME PROCESSES:" -ForegroundColor Yellow
$gameProcs = Get-Process -Name "AcrGame*","NesysService*" -ErrorAction SilentlyContinue
if ($gameProcs) {
    foreach ($p in $gameProcs) {
        Write-Host "  $($p.ProcessName) PID=$($p.Id)" -ForegroundColor Gray
    }
} else {
    Write-Host "  No game processes running" -ForegroundColor Gray
}

Write-Host "`n============================================" -ForegroundColor Cyan
