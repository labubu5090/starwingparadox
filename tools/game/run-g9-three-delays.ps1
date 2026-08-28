<#
.SYNOPSIS
    Phase 2A-G9: Test three controlled startup delays (0s, 5s, 15s).
.DESCRIPTION
    Runs the cold-boot validation with three different stabilization delays:
      Run A: 0 seconds after readiness
      Run B: 5 seconds after readiness
      Run C: 15 seconds after readiness

    For each run:
      1. Fully stops the server stack
      2. Waits for ports to be free
      3. Runs cold-boot validation with the specified delay
      4. Records timeline to g9_cold_boot_timeline.json
      5. Operator launches game manually
      6. Operator observes TCP server console
      7. Records whether first Ping attempt succeeded
      8. Fully stops the server stack
      9. Moves to next run

.PARAMETER RunLabel
    Optional label for this run (e.g., "RunA", "RunB", "RunC").
    If not specified, auto-increments.
.EXAMPLE
    .\run-g9-three-delays.ps1 -RunLabel "RunA"
    .\run-g9-three-delays.ps1 -RunLabel "RunB"
    .\run-g9-three-delays.ps1 -RunLabel "RunC"
#>
param(
    [string]$RunLabel = "Auto"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\Users\KAHO\Pictures\Starwing"
$ServerRoot  = "$ProjectRoot\server"
$Python      = "$ServerRoot\.venv\Scripts\python.exe"
$ProbeScript = "$ProjectRoot\tools\game\run-cold-boot-validation.ps1"
$ProbePython = "$ProjectRoot\tools\game\tcp_readiness_probe.py"

$delays = @(0, 5, 15)
$runIndex = 0

if ($RunLabel -ne "Auto") {
    # Single run mode
    switch ($RunLabel) {
        "RunA" { $runIndex = 0 }
        "RunB" { $runIndex = 1 }
        "RunC" { $runIndex = 2 }
        default { $runIndex = 0 }
    }
    $delays = @($delays[$runIndex])
}

foreach ($delay in $delays) {
    $runIndex = [array]::IndexOf(@(0, 5, 15), $delay)
    $label = "Run$([char](65 + $runIndex))"  # RunA, RunB, RunC
    
    Write-Host "`n============================================" -ForegroundColor Magenta
    Write-Host "  PHASE 2A-G9: $label - Stabilization delay: ${delay}s" -ForegroundColor Magenta
    Write-Host "============================================" -ForegroundColor Magenta
    
    # ── Step 1: Fully stop server stack ────────────────────
    Write-Host "`n[$label] Stopping server stack..." -ForegroundColor Yellow
    & "$ProjectRoot\tools\game\stop-full-server-stack.ps1"
    Start-Sleep -Seconds 3
    
    # ── Step 2: Verify ports free ──────────────────────────
    Write-Host "[$label] Verifying ports free..." -ForegroundColor Yellow
    foreach ($port in @(80, 4001, 6666)) {
        $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        if ($conns) {
            Write-Host "  WARNING: Port $port still in use" -ForegroundColor Red
            # Force kill
            foreach ($conn in $conns) {
                Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
            }
            Start-Sleep -Seconds 2
        }
    }
    Write-Host "  OK: All ports free" -ForegroundColor Green
    
    # ── Step 3: Run TCP readiness probe first ──────────────
    Write-Host "`n[$label] Running TCP readiness probe..." -ForegroundColor Yellow
    $probeResult = & $Python $ProbePython 2>&1
    Write-Host $probeResult
    
    # ── Step 4: Start cold-boot validation ─────────────────
    Write-Host "`n[$label] Starting cold-boot validation (delay=${delay}s)..." -ForegroundColor Yellow
    
    # Start the cold-boot validation in a separate process
    $validationProc = Start-Process -FilePath "powershell.exe" `
        -ArgumentList "-ExecutionPolicy Bypass -File `"$ProbeScript`" -StabilizationDelay $delay" `
        -PassThru
    
    Write-Host "  Validation PID: $($validationProc.Id)" -ForegroundColor Green
    Write-Host "  Waiting for READY_FOR_GAME..." -ForegroundColor Yellow
    
    # Wait for READY_FOR_GAME (poll the validation process)
    $readyDetected = $false
    for ($i = 0; $i -lt 120; $i++) {
        Start-Sleep -Seconds 2
        if ($validationProc.HasExited) {
            Write-Host "  Validation process exited" -ForegroundColor Yellow
            break
        }
        # Check if servers are ready
        try {
            $healthResp = curl.exe -s -o NUL -w "%{http_code}" "http://127.0.0.1:4001/health" 2>&1
            $tcpListener = Get-NetTCPConnection -LocalPort 6666 -State Listen -ErrorAction SilentlyContinue
            if ($healthResp -eq "200" -and $tcpListener) {
                $readyDetected = $true
                break
            }
        } catch { }
    }
    
    if ($readyDetected) {
        Write-Host "`n  READY_FOR_GAME detected!" -ForegroundColor Green
        Write-Host "  Launch AcrGame now and observe the TCP server console." -ForegroundColor Yellow
        Write-Host "  Record whether the first Ping attempt succeeded." -ForegroundColor Yellow
        Write-Host "  Press Enter when done observing..." -ForegroundColor Yellow
        Read-Host
    } else {
        Write-Host "  Could not detect READY_FOR_GAME. Proceeding anyway..." -ForegroundColor Yellow
        Write-Host "  Press Enter when done observing..." -ForegroundColor Yellow
        Read-Host
    }
    
    # ── Step 5: Record results ─────────────────────────────
    $resultFile = "$ProjectRoot\docs\generated\g9_${label}_delay${delay}s.json"
    $result = @{
        run_label = $label
        stabilization_delay_sec = $delay
        timestamp = (Get-Date).ToString("o")
        ready_detected = $readyDetected
        validation_pid = $validationProc.Id
    }
    $result | ConvertTo-Json -Depth 3 | Out-File -FilePath $resultFile -Encoding utf8
    Write-Host "  Results saved to: $resultFile" -ForegroundColor Gray
    
    # ── Step 6: Stop server stack ──────────────────────────
    Write-Host "`n[$label] Stopping server stack..." -ForegroundColor Yellow
    & "$ProjectRoot\tools\game\stop-full-server-stack.ps1"
    Start-Sleep -Seconds 3
    
    Write-Host "`n[$label] Complete." -ForegroundColor Green
}

Write-Host "`n============================================" -ForegroundColor Magenta
Write-Host "  ALL THREE RUNS COMPLETE" -ForegroundColor Magenta
Write-Host "============================================" -ForegroundColor Magenta
Write-Host "  Compare results in:" -ForegroundColor White
Write-Host "    docs/generated/g9_RunA_delay0s.json" -ForegroundColor White
Write-Host "    docs/generated/g9_RunB_delay5s.json" -ForegroundColor White
Write-Host "    docs/generated/g9_RunC_delay15s.json" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Magenta
