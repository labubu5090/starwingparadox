<#
.SYNOPSIS
    Start the complete Starwing server stack in three visible console windows.
.DESCRIPTION
    Launches:
      Window 1: FastAPI HTTP server  127.0.0.1:4001
      Window 2: HTTP reverse proxy   127.0.0.1:80
      Window 3: Matching TCP server  0.0.0.0:6666
    Each window stays open and displays live logs.
.PARAMETER SkipProxy
    Skip the HTTP proxy.
.EXAMPLE
    .\start-full-server-stack.ps1
    .\start-full-server-stack.ps1 -SkipProxy
#>
param(
    [switch]$SkipProxy
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\Users\KAHO\Pictures\Starwing"
$ServerRoot  = "$ProjectRoot\server"
$Python      = "$ServerRoot\.venv\Scripts\python.exe"
$PidDir      = "$ServerRoot\data"
$PidFileHTTP = "$PidDir\http_server.pid"
$PidFileProxy= "$PidDir\http_proxy.pid"
$PidFileTCP  = "$PidDir\tcp_server.pid"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  STARWING FULL SERVER STACK LAUNCHER" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ── Validate prerequisites ──────────────────────────────
Write-Host "`n[1/5] Validating prerequisites..." -ForegroundColor Yellow

if (-not (Test-Path $Python)) {
    Write-Host "FATAL: Python not found at $Python" -ForegroundColor Red
    exit 1
}
Write-Host "  OK: Python found" -ForegroundColor Green

$requiredFiles = @(
    "$ServerRoot\app\main.py",
    "$ServerRoot\app\tcp_server.py",
    "$ProjectRoot\tools\game\proxy_to_4001.py"
)
foreach ($f in $requiredFiles) {
    if (-not (Test-Path $f)) {
        Write-Host "FATAL: Not found: $f" -ForegroundColor Red
        exit 1
    }
}
Write-Host "  OK: All entry points found" -ForegroundColor Green

# ── Check for stale processes on the ports ───────────────
Write-Host "`n[2/5] Checking ports..." -ForegroundColor Yellow

$portsOk = $true
$portsToCheck = @(4001, 6666)
if (-not $SkipProxy) { $portsToCheck += 80 }

foreach ($port in $portsToCheck) {
    $existing = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($existing) {
        foreach ($conn in $existing) {
            $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            $name = if ($proc) { $proc.Name } else { "PID $($conn.OwningProcess)" }
            Write-Host "  ERROR: Port $port already in use by $name" -ForegroundColor Red
        }
        $portsOk = $false
    } else {
        Write-Host "  OK: Port $port free" -ForegroundColor Green
    }
}

if (-not $portsOk) {
    Write-Host "`nFATAL: Required ports are occupied." -ForegroundColor Red
    Write-Host "Run .\stop-full-server-stack.ps1 first." -ForegroundColor Yellow
    exit 1
}

# ── Create PID directory ─────────────────────────────────
if (-not (Test-Path $PidDir)) {
    New-Item -ItemType Directory -Path $PidDir -Force | Out-Null
}

# ── Clean stale PID files ────────────────────────────────
foreach ($pf in @($PidFileHTTP, $PidFileProxy, $PidFileTCP)) {
    if (Test-Path $pf) { Remove-Item $pf -Force }
}

# ── Start Window 1: FastAPI HTTP server ──────────────────
Write-Host "`n[3/5] Starting HTTP server on 127.0.0.1:4001..." -ForegroundColor Yellow

$httpProc = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/k", "title STARWING HTTP SERVER :4001 && cd /d `"$ServerRoot`" && `"$Python`" -m uvicorn app.main:app --host 127.0.0.1 --port 4001 --log-level info" `
    -PassThru

$httpProc.Id | Out-File -FilePath $PidFileHTTP -Encoding ascii -NoNewline
Write-Host "  PID: $($httpProc.Id)" -ForegroundColor Green

# ── Start Window 2: HTTP reverse proxy ───────────────────
$proxyProc = $null
if (-not $SkipProxy) {
    Write-Host "`n[4/5] Starting HTTP proxy on 127.0.0.1:80..." -ForegroundColor Yellow

    $proxyProc = Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/k", "title STARWING HTTP PROXY :80 && cd /d `"$ServerRoot`" && `"$Python`" `"$ProjectRoot\tools\game\proxy_to_4001.py`"" `
        -PassThru

    $proxyProc.Id | Out-File -FilePath $PidFileProxy -Encoding ascii -NoNewline
    Write-Host "  PID: $($proxyProc.Id)" -ForegroundColor Green
} else {
    Write-Host "`n[4/5] Skipping proxy (-SkipProxy)" -ForegroundColor Yellow
}

# ── Start Window 3: Matching TCP server ──────────────────
Write-Host "`n[5/5] Starting TCP server on 0.0.0.0:6666..." -ForegroundColor Yellow

$tcpProc = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/k", "title STARWING MATCHING TCP :6666 && cd /d `"$ServerRoot`" && `"$Python`" -m app.tcp_server" `
    -PassThru

$tcpProc.Id | Out-File -FilePath $PidFileTCP -Encoding ascii -NoNewline
Write-Host "  PID: $($tcpProc.Id)" -ForegroundColor Green

# ── Wait for servers to become ready ─────────────────────
Write-Host "`nWaiting for servers to start (10 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# ── Verify HTTP server ──────────────────────────────────
Write-Host "`n=== VERIFICATION ===" -ForegroundColor Cyan

$httpAlive = $false
try {
    $resp = curl.exe -s -o NUL -w "%{http_code}" "http://127.0.0.1:4001/health" 2>&1
    $httpAlive = $resp -eq "200"
    Write-Host "  HTTP :4001 /health : $resp" -ForegroundColor $(if ($httpAlive) {'Green'} else {'Red'})
} catch {
    Write-Host "  HTTP :4001 /health : FAILED" -ForegroundColor Red
}

# ── Verify proxy ─────────────────────────────────────────
$proxyAlive = $false
if (-not $SkipProxy) {
    try {
        $resp = curl.exe -s -o NUL -w "%{http_code}" "http://dev.starwing.jp/mock/health" 2>&1
        $proxyAlive = $resp -eq "200"
        Write-Host "  PROXY :80  dev.starwing.jp : $resp" -ForegroundColor $(if ($proxyAlive) {'Green'} else {'Red'})
    } catch {
        Write-Host "  PROXY :80  dev.starwing.jp : FAILED" -ForegroundColor Red
    }
}

# ── Verify TCP ───────────────────────────────────────────
$tcpListening = Get-NetTCPConnection -LocalPort 6666 -State Listen -ErrorAction SilentlyContinue
if ($tcpListening) {
    Write-Host "  TCP  :6666 LISTENING" -ForegroundColor Green
} else {
    Write-Host "  TCP  :6666 NOT LISTENING" -ForegroundColor Red
}

# ── Verify matching endpoint ─────────────────────────────
try {
    $body = curl.exe -s -X POST "http://dev.starwing.jp/mock/matching/server" -H "Content-Type: application/octet-stream" 2>&1
    Write-Host "  MATCH: $body" -ForegroundColor Green
} catch {
    Write-Host "  MATCH: FAILED" -ForegroundColor Red
}

# ── Final status ─────────────────────────────────────────
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  STACK STATUS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  HTTP Server :4001  PID=$($httpProc.Id)  $(if ($httpAlive) {'ALIVE'} else {'FAILED'})" -ForegroundColor $(if ($httpAlive) {'Green'} else {'Red'})
if ($proxyProc) {
    Write-Host "  HTTP Proxy  :80   PID=$($proxyProc.Id) $(if ($proxyAlive) {'ALIVE'} else {'FAILED'})" -ForegroundColor $(if ($proxyAlive) {'Green'} else {'Red'})
} else {
    Write-Host "  HTTP Proxy  :80   SKIPPED" -ForegroundColor Yellow
}
Write-Host "  TCP Server  :6666 PID=$($tcpProc.Id)  $(if ($tcpListening) {'LISTENING'} else {'FAILED'})" -ForegroundColor $(if ($tcpListening) {'Green'} else {'Red'})
Write-Host "============================================" -ForegroundColor Cyan

if ((-not $httpAlive) -or ((-not $SkipProxy) -and (-not $proxyAlive)) -or (-not $tcpListening)) {
    Write-Host "`nWARNING: One or more servers failed to start." -ForegroundColor Red
    Write-Host "Check the console windows for errors." -ForegroundColor Yellow
} else {
    Write-Host "`nAll servers started successfully." -ForegroundColor Green
}

Write-Host "`nThree console windows should now be visible:" -ForegroundColor Cyan
Write-Host "  1. STARWING HTTP SERVER :4001" -ForegroundColor White
Write-Host "  2. STARWING HTTP PROXY :80" -ForegroundColor White
Write-Host "  3. STARWING MATCHING TCP :6666" -ForegroundColor White
Write-Host "`nDo NOT close them. They are your live server logs." -ForegroundColor Yellow
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Run .\check-full-server-stack.ps1 to confirm" -ForegroundColor White
Write-Host "  2. Launch AcrGame.exe manually" -ForegroundColor White
Write-Host "  3. Observe which console receives traffic" -ForegroundColor White
Write-Host "  4. When done, run .\stop-full-server-stack.ps1" -ForegroundColor White
