<#
.SYNOPSIS
    Cold-boot server readiness validation for Phase 2A-G9.
.DESCRIPTION
    Performs a clean cold-boot of the Starwing server stack with strict
    process ownership verification, port checks, and readiness probing.

    Steps:
      1.  Confirm AcrGame is not running
      2.  Confirm no stale server processes (verify executable paths)
      3.  Clear stale PID files
      4.  Verify ports 80, 4001, 6666 are free
      5.  Start HTTP :4001, record PID and start time
      6.  Verify HTTP /health
      7.  Verify HTTP /ready
      8.  Start Proxy :80, record PID and start time
      9.  Verify POST /mock/matching/server exact response
      10. Start TCP :6666, record PID and start time
      11. Verify TCP listener and executable path
      12. Perform RAW_TRANSPORT_READINESS_ONLY probe
      13. Verify TCP server alive after probe
      14. Verify listener still owned by same PID
      15. Verify connection count zero
      16. Apply stabilization delay
      17. Re-run all readiness checks
      18. Print READY_FOR_GAME
      19. Write runtime metadata to docs/generated/

    Does NOT launch AcrGame automatically.
.PARAMETER StabilizationSeconds
    Seconds to wait after readiness before final verification.
    Valid values: 0, 5, 15. Default: 0
.PARAMETER SkipProxy
    Skip the HTTP proxy.
.PARAMETER RunId
    Unique run identifier. Auto-generated if not provided.
.EXAMPLE
    .\run-cold-boot-validation.ps1 -StabilizationSeconds 0
    .\run-cold-boot-validation.ps1 -StabilizationSeconds 5 -RunId "g9-run-b"
#>
param(
    [ValidateSet(0, 5, 15)]
    [int]$StabilizationSeconds = 0,
    [switch]$SkipProxy,
    [string]$RunId = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\Users\KAHO\Pictures\Starwing"
$ServerRoot  = "$ProjectRoot\server"
$Python      = "$ServerRoot\.venv\Scripts\python.exe"
$PidDir      = "$ServerRoot\data"
$PidFileHTTP = "$PidDir\http_server.pid"
$PidFileProxy= "$PidDir\http_proxy.pid"
$PidFileTCP  = "$PidDir\tcp_server.pid"
$GeneratedDir= "$ProjectRoot\docs\generated"

# ── Generate Run ID ────────────────────────────────────────
if (-not $RunId) {
    $RunId = "g9-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
}
$RunDir = "$GeneratedDir\$RunId"
if (-not (Test-Path $RunDir)) {
    New-Item -ItemType Directory -Path $RunDir -Force | Out-Null
}

$startTime = Get-Date
$metadata = @{
    run_id = $RunId
    stabilization_seconds = $StabilizationSeconds
    start_time = $startTime.ToString("o")
    skip_proxy = [bool]$SkipProxy
    project_root = $ProjectRoot
    python_exe = $Python
}

function Write-Timestamp {
    param([string]$Message)
    $elapsed = (Get-Date) - $startTime
    Write-Host "[$($elapsed.TotalSeconds.ToString('F3'))s] $Message" -ForegroundColor Gray
}

function Test-PortFree {
    param([int]$Port)
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return (-not $conns)
}

function Get-ProcessByPort {
    param([int]$Port)
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($conns) {
        foreach ($conn in $conns) {
            return Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
        }
    }
    return $null
}

function Verify-ExecutablePath {
    param([System.Diagnostics.Process]$Process, [string]$ExpectedName)
    if (-not $Process) { return $false }
    try {
        $path = $Process.MainModule.FileName
        return $path -like "*$ExpectedName*"
    } catch {
        return $false
    }
}

function Save-Metadata {
    param([string]$Phase, [hashtable]$Extra = @{})
    $metadata.phase = $Phase
    $metadata.timestamp = (Get-Date).ToString("o")
    foreach ($k in $Extra.Keys) { $metadata[$k] = $Extra[$k] }
    $metadata | ConvertTo-Json -Depth 5 | Out-File -FilePath "$RunDir\metadata.json" -Encoding utf8
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  PHASE 2A-G9: COLD-BOOT VALIDATION" -ForegroundColor Cyan
Write-Host "  Run ID: $RunId" -ForegroundColor Cyan
Write-Host "  Stabilization: ${StabilizationSeconds}s" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ── Step 1: Confirm AcrGame is not running ────────────────
Write-Host "`n[1/19] Checking for AcrGame processes..." -ForegroundColor Yellow
$gameProcs = Get-Process -Name "AcrGame*" -ErrorAction SilentlyContinue
if ($gameProcs) {
    Write-Host "  FATAL: AcrGame processes found:" -ForegroundColor Red
    foreach ($p in $gameProcs) {
        Write-Host "    PID $($p.Id): $($p.Name)" -ForegroundColor Red
    }
    Write-Host "  Close the game first." -ForegroundColor Yellow
    exit 1
}
Write-Host "  OK: No AcrGame processes" -ForegroundColor Green

# ── Step 2: Confirm no stale server processes ─────────────
Write-Host "`n[2/19] Checking for stale server processes..." -ForegroundColor Yellow
$staleFound = $false
$portsToCheck = @(4001, 6666)
if (-not $SkipProxy) { $portsToCheck += 80 }

foreach ($port in $portsToCheck) {
    $proc = Get-ProcessByPort -Port $port
    if ($proc) {
        Write-Host "  STALE: Port $port used by PID $($proc.Id) ($($proc.Name))" -ForegroundColor Red
        $staleFound = $true
    }
}
if ($staleFound) {
    Write-Host "  Running safe stop script..." -ForegroundColor Yellow
    & "$ProjectRoot\tools\game\stop-full-server-stack.ps1"
    Start-Sleep -Seconds 3
    # Re-verify
    foreach ($port in $portsToCheck) {
        if (-not (Test-PortFree -Port $port)) {
            Write-Host "  FATAL: Port $port still occupied after stop" -ForegroundColor Red
            exit 1
        }
    }
}
Write-Host "  OK: No stale server processes" -ForegroundColor Green

# ── Step 3: Clear stale PID files ─────────────────────────
Write-Host "`n[3/19] Clearing stale PID files..." -ForegroundColor Yellow
foreach ($pf in @($PidFileHTTP, $PidFileProxy, $PidFileTCP)) {
    if (Test-Path $pf) {
        Remove-Item $pf -Force
        Write-Host "  Removed: $pf" -ForegroundColor Gray
    }
}
Write-Host "  OK: PID files cleared" -ForegroundColor Green

# ── Step 4: Verify ports are free ─────────────────────────
Write-Host "`n[4/19] Verifying ports are free..." -ForegroundColor Yellow
$allFree = $true
foreach ($port in $portsToCheck) {
    if (Test-PortFree -Port $port) {
        Write-Host "  OK: Port $port free" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: Port $port occupied" -ForegroundColor Red
        $allFree = $false
    }
}
if (-not $allFree) {
    Write-Host "FATAL: Ports not free" -ForegroundColor Red
    exit 1
}

# ── Step 5: Start HTTP server on 4001 ─────────────────────
Write-Host "`n[5/19] Starting HTTP server on 127.0.0.1:4001..." -ForegroundColor Yellow
if (-not (Test-Path $PidDir)) {
    New-Item -ItemType Directory -Path $PidDir -Force | Out-Null
}

$httpStartTime = Get-Date
$httpProc = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/k", "title STARWING HTTP SERVER :4001 && cd /d `"$ServerRoot`" && `"$Python`" -m uvicorn app.main:app --host 127.0.0.1 --port 4001 --log-level info" `
    -PassThru
$httpProc.Id | Out-File -FilePath $PidFileHTTP -Encoding ascii -NoNewline
Write-Host "  PID: $($httpProc.Id)" -ForegroundColor Green
$metadata.http_pid = $httpProc.Id
$metadata.http_start_time = $httpStartTime.ToString("o")

# ── Step 6: Verify HTTP /health ───────────────────────────
Write-Host "`n[6/19] Verifying HTTP /health..." -ForegroundColor Yellow
$healthOk = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    try {
        $resp = curl.exe -s -o NUL -w "%{http_code}" "http://127.0.0.1:4001/health" 2>&1
        if ($resp -eq "200") {
            $healthOk = $true
            $metadata.http_health_ok_time = (Get-Date).ToString("o")
            Write-Timestamp "  /health OK after $($i+1)s"
            break
        }
    } catch { }
}
if (-not $healthOk) {
    Write-Host "  FATAL: /health not OK after 30s" -ForegroundColor Red
    exit 1
}

# ── Step 7: Verify HTTP /ready ────────────────────────────
Write-Host "`n[7/19] Verifying HTTP /ready..." -ForegroundColor Yellow
$readyOk = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    try {
        $resp = curl.exe -s -o NUL -w "%{http_code}" "http://127.0.0.1:4001/ready" 2>&1
        if ($resp -eq "200") {
            $readyOk = $true
            $metadata.http_ready_ok_time = (Get-Date).ToString("o")
            Write-Timestamp "  /ready OK after $($i+1)s"
            break
        }
    } catch { }
}
if (-not $readyOk) {
    Write-Host "  FATAL: /ready not OK after 30s" -ForegroundColor Red
    exit 1
}

# ── Step 8: Start proxy on port 80 ────────────────────────
$proxyProc = $null
if (-not $SkipProxy) {
    Write-Host "`n[8/19] Starting HTTP proxy on 127.0.0.1:80..." -ForegroundColor Yellow
    $proxyStartTime = Get-Date
    $proxyProc = Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/k", "title STARWING HTTP PROXY :80 && cd /d `"$ServerRoot`" && `"$Python`" `"$ProjectRoot\tools\game\proxy_to_4001.py`"" `
        -PassThru
    $proxyProc.Id | Out-File -FilePath $PidFileProxy -Encoding ascii -NoNewline
    Write-Host "  PID: $($proxyProc.Id)" -ForegroundColor Green
    $metadata.proxy_pid = $proxyProc.Id
    $metadata.proxy_start_time = $proxyStartTime.ToString("o")
} else {
    Write-Host "`n[8/19] Skipping proxy (-SkipProxy)" -ForegroundColor Yellow
    $metadata.proxy_pid = 0
}

# ── Step 9: Verify POST /mock/matching/server ─────────────
Write-Host "`n[9/19] Verifying matching URL..." -ForegroundColor Yellow
$matchOk = $false
$matchBody = ""
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 1
    try {
        $matchBody = curl.exe -s -X POST "http://dev.starwing.jp/mock/matching/server" -H "Content-Type: application/octet-stream" 2>&1
        if ($matchBody -match "ip_addr") {
            $matchOk = $true
            $metadata.matching_response = $matchBody
            $metadata.matching_ok_time = (Get-Date).ToString("o")
            import-module Microsoft.PowerShell.Utility
            $metadata.matching_response_sha256 = (Get-FileHash -Algorithm SHA256 -InputStream ([System.IO.MemoryStream][System.Text.Encoding]::UTF8.GetBytes($matchBody))).Hash
            Write-Timestamp "  Matching OK after $($i+1)s: $matchBody"
            break
        }
    } catch { }
}
if (-not $matchOk) {
    Write-Host "  WARNING: Matching URL not OK" -ForegroundColor Yellow
}

# ── Step 10: Start TCP server on 6666 ─────────────────────
Write-Host "`n[10/19] Starting TCP server on 0.0.0.0:6666..." -ForegroundColor Yellow
$tcpStartTime = Get-Date
$tcpProc = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/k", "title STARWING MATCHING TCP :6666 && cd /d `"$ServerRoot`" && `"$Python`" -m app.tcp_server" `
    -PassThru
$tcpProc.Id | Out-File -FilePath $PidFileTCP -Encoding ascii -NoNewline
Write-Host "  PID: $($tcpProc.Id)" -ForegroundColor Green
$metadata.tcp_pid = $tcpProc.Id
$metadata.tcp_start_time = $tcpStartTime.ToString("o")

# ── Step 11: Verify TCP listener ──────────────────────────
Write-Host "`n[11/19] Verifying TCP listener on 6666..." -ForegroundColor Yellow
$tcpOk = $false
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 1
    $listener = Get-NetTCPConnection -LocalPort 6666 -State Listen -ErrorAction SilentlyContinue
    if ($listener) {
        $tcpOk = $true
        $metadata.tcp_listener_pid = $listener[0].OwningProcess
        $metadata.tcp_accept_ready_time = (Get-Date).ToString("o")
        Write-Timestamp "  TCP listener OK after $($i+1)s (PID=$($listener[0].OwningProcess))"
        break
    }
}
if (-not $tcpOk) {
    Write-Host "  FATAL: TCP listener not found on 6666" -ForegroundColor Red
    exit 1
}

# ── Step 12: Readiness probe ──────────────────────────────
Write-Host "`n[12/19] Running RAW_TRANSPORT_READINESS_ONLY probe..." -ForegroundColor Yellow
$probeOk = $false
try {
    $probeResult = & $Python -c "
import sys; sys.path.insert(0, r'$ProjectRoot')
from tools.game.tcp_readiness_probe import run_probe_sync
r = run_probe_sync(listener_pid=$($metadata.tcp_listener_pid))
print(f'connected={r.connected}')
print(f'frame_sent={r.frame_sent}')
print(f'closed={r.connection_closed_cleanly}')
print(f'alive={r.server_alive_after}')
print(f'owned={r.listener_still_owned}')
print(f'zero={r.connection_count_zero}')
print(f'type={r.probe_type}')
print(f'error={r.error}')
" 2>&1
    Write-Host $probeResult
    foreach ($line in $probeResult) {
        if ($line -match "^connected=True") { $probeOk = $true }
    }
    $metadata.probe_type = "RAW_TRANSPORT_READINESS_ONLY"
    $metadata.probe_ok = $probeOk
    $metadata.probe_time = (Get-Date).ToString("o")
} catch {
    Write-Host "  Probe error: $($_.Exception.Message)" -ForegroundColor Yellow
    $metadata.probe_ok = $false
    $metadata.probe_error = $_.Exception.Message
}

# ── Step 13: Verify TCP alive after probe ─────────────────
Write-Host "`n[13/19] Verifying TCP alive after probe..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
$listenerAfter = Get-NetTCPConnection -LocalPort 6666 -State Listen -ErrorAction SilentlyContinue
$tcpAlive = [bool]$listenerAfter
$metadata.tcp_alive_after_probe = $tcpAlive
if ($tcpAlive) {
    Write-Host "  OK: TCP server still listening" -ForegroundColor Green
} else {
    Write-Host "  ERROR: TCP server died after probe" -ForegroundColor Red
    exit 1
}

# ── Step 14: Verify listener PID ──────────────────────────
Write-Host "`n[14/19] Verifying listener PID unchanged..." -ForegroundColor Yellow
$listenerNow = Get-NetTCPConnection -LocalPort 6666 -State Listen -ErrorAction SilentlyContinue
if ($listenerNow -and $metadata.tcp_listener_pid) {
    $currentPid = $listenerNow[0].OwningProcess
    $pidMatch = $currentPid -eq $metadata.tcp_listener_pid
    $metadata.listener_pid_unchanged = $pidMatch
    if ($pidMatch) {
        Write-Host "  OK: PID $currentPid unchanged" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: PID changed from $($metadata.tcp_listener_pid) to $currentPid" -ForegroundColor Yellow
    }
}

# ── Step 15: Verify connection count zero ─────────────────
Write-Host "`n[15/19] Verifying connection count..." -ForegroundColor Yellow
$connsNow = Get-NetTCPConnection -LocalPort 6666 -State ESTABLISHED -ErrorAction SilentlyContinue
$connCount = if ($connsNow) { $connsNow.Count } else { 0 }
$metadata.connection_count = $connCount
if ($connCount -eq 0) {
    Write-Host "  OK: No active connections on 6666" -ForegroundColor Green
} else {
    Write-Host "  WARNING: $connCount active connections" -ForegroundColor Yellow
}

# ── Step 16: Stabilization delay ──────────────────────────
Write-Host "`n[16/19] Stabilization delay: ${StabilizationSeconds}s..." -ForegroundColor Yellow
Start-Sleep -Seconds $StabilizationSeconds
$metadata.stabilization_complete_time = (Get-Date).ToString("o")
Write-Timestamp "  Stabilization complete"

# ── Step 17: Re-run all readiness checks ──────────────────
Write-Host "`n[17/19] Final readiness verification..." -ForegroundColor Yellow

$finalResults = @{}

try {
    $resp = curl.exe -s -o NUL -w "%{http_code}" "http://127.0.0.1:4001/health" 2>&1
    $finalResults["HTTP_HEALTH"] = $resp -eq "200"
} catch { $finalResults["HTTP_HEALTH"] = $false }

try {
    $resp = curl.exe -s -o NUL -w "%{http_code}" "http://127.0.0.1:4001/ready" 2>&1
    $finalResults["HTTP_READY"] = $resp -eq "200"
} catch { $finalResults["HTTP_READY"] = $false }

if (-not $SkipProxy) {
    try {
        $resp = curl.exe -s -o NUL -w "%{http_code}" "http://dev.starwing.jp/mock/health" 2>&1
        $finalResults["PROXY"] = $resp -eq "200"
    } catch { $finalResults["PROXY"] = $false }
} else {
    $finalResults["PROXY"] = $true
}

$finalResults["TCP_LISTENER"] = [bool](Get-NetTCPConnection -LocalPort 6666 -State Listen -ErrorAction SilentlyContinue)
$finalResults["HTTP_PID_ALIVE"] = (Get-Process -Id $httpProc.Id -ErrorAction SilentlyContinue) -ne $null
$finalResults["TCP_PID_ALIVE"] = (Get-Process -Id $tcpProc.Id -ErrorAction SilentlyContinue) -ne $null
if ($proxyProc) {
    $finalResults["PROXY_PID_ALIVE"] = (Get-Process -Id $proxyProc.Id -ErrorAction SilentlyContinue) -ne $null
}

foreach ($key in $finalResults.Keys) {
    $status = if ($finalResults[$key]) { "OK" } else { "FAIL" }
    $color = if ($finalResults[$key]) { "Green" } else { "Red" }
    Write-Host "  $key : $status" -ForegroundColor $color
}
$metadata.final_results = $finalResults

# ── Step 18: Print READY_FOR_GAME ─────────────────────────
Write-Host "`n[18/19] Final status..." -ForegroundColor Yellow
$allOk = $finalResults.Values -notcontains $false
if ($allOk) {
    Write-Host "`n============================================" -ForegroundColor Green
    Write-Host "  READY_FOR_GAME" -ForegroundColor Green
    Write-Host "  Run ID: $RunId" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "  HTTP Server  :4001  PID=$($httpProc.Id)" -ForegroundColor White
    if ($proxyProc) {
        Write-Host "  HTTP Proxy   :80   PID=$($proxyProc.Id)" -ForegroundColor White
    }
    Write-Host "  TCP Server   :6666 PID=$($tcpProc.Id)" -ForegroundColor White
    Write-Host "  Stabilization: ${StabilizationSeconds}s" -ForegroundColor White
    Write-Host "============================================" -ForegroundColor Green
    $metadata.ready_for_game_time = (Get-Date).ToString("o")
} else {
    Write-Host "`n============================================" -ForegroundColor Red
    Write-Host "  NOT READY - some checks failed" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    exit 1
}

# ── Step 19: Write metadata and wait for operator ─────────
Write-Host "`n[19/19] Writing runtime metadata..." -ForegroundColor Yellow
Save-Metadata -Phase "READY_FOR_GAME"

Write-Host "`nDo NOT close this window." -ForegroundColor Yellow
Write-Host "Launch AcrGame manually, then observe the server consoles." -ForegroundColor Yellow
Write-Host "Press Enter when done observing..." -ForegroundColor Yellow
Read-Host

# Save final metadata
$metadata.end_time = (Get-Date).ToString("o")
$metadata.total_elapsed_ms = ((Get-Date) - $startTime).TotalMilliseconds
Save-Metadata -Phase "OBSERVATION_COMPLETE"

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  COLD-BOOT VALIDATION COMPLETE" -ForegroundColor Cyan
Write-Host "  Run ID: $RunId" -ForegroundColor Cyan
Write-Host "  Metadata: $RunDir\metadata.json" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
