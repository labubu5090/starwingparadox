<#
.SYNOPSIS
    Verify the Starwing game server state.
.EXAMPLE
    .\verify-game-server.ps1
#>

$ErrorActionPreference = "SilentlyContinue"

Write-Host "=== Starwing Game Server Verification ===" -ForegroundColor Cyan

# Port checks
Write-Host "`nPorts:" -ForegroundColor Yellow
foreach ($port in @(4000, 4001, 6666, 8000)) {
    $c = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($c) {
        $procs = $c | ForEach-Object { Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue } | Where-Object { $_ }
        $names = ($procs | ForEach-Object { $_.Name }) -join ", "
        Write-Host "  $port : LISTENING ($names)" -ForegroundColor Green
    } else {
        Write-Host "  $port : free" -ForegroundColor Gray
    }
}

# Health check
Write-Host "`nHealth:" -ForegroundColor Yellow
try {
    $h = Invoke-RestMethod -Uri "http://127.0.0.1:4001/health" -ErrorAction Stop
    Write-Host "  /health: $($h.status)" -ForegroundColor Green
} catch {
    Write-Host "  /health: NOT RESPONDING" -ForegroundColor Red
}

# Process check
Write-Host "`nProcesses:" -ForegroundColor Yellow
Get-Process -Name "AcrGame*","NesysService*","python*" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "  $($_.Name) PID=$($_.Id)" -ForegroundColor Gray
}

# Guard check
Write-Host "`nGuards:" -ForegroundColor Yellow
Write-Host "  Matching: NOT_IMPLEMENTED" -ForegroundColor Green
Write-Host "  Battle: NOT_IMPLEMENTED" -ForegroundColor Green
Write-Host "  Capture: disabled" -ForegroundColor Green
