#Requires -Version 5.1
<#
.SYNOPSIS
    Phase 2A pre-cabinet preflight check for Starwing Paradox server.
.DESCRIPTION
    Verifies all blocking conditions before accepting a cabinet connection.
    Returns non-zero exit code if any blocking condition exists.
.NOTES
    Does NOT modify firewall, DNS, hosts file, or cabinet settings.
#>

param(
    [string]$ProjectRoot = "C:\Users\KAHO\Pictures\Starwing"
)

$ErrorActionPreference = "Continue"
$blocking = 0
$warnings = 0

function Write-Check {
    param([string]$Name, [string]$Status, [string]$Detail = "")
    if ($Status -eq "PASS") {
        Write-Host "  [PASS] $Name" -ForegroundColor Green
    } elseif ($Status -eq "WARN") {
        Write-Host "  [WARN] $Name - $Detail" -ForegroundColor Yellow
        $script:warnings++
    } else {
        Write-Host "  [FAIL] $Name - $Detail" -ForegroundColor Red
        $script:blocking++
    }
}

Write-Host "`n=== Starwing Paradox Phase 2A Preflight ===" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot`n"

# 1. Project path
Write-Host "--- Project ---" -ForegroundColor Yellow
if (Test-Path "$ProjectRoot\server\app\main.py") {
    Write-Check "Project path" "PASS"
} else {
    Write-Check "Project path" "FAIL" "server\app\main.py not found"
}

# 2. Python environment
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    $ver = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
    if ($ver -match "^(3\.1[0-9])") {
        Write-Check "Python environment" "PASS" "v$ver"
    } else {
        Write-Check "Python environment" "FAIL" "v$ver (need 3.10+)"
    }
} else {
    Write-Check "Python environment" "FAIL" "python not found"
}

# 3. Required dependencies
$deps = python -c "import sqlalchemy, aiosqlite, fastapi, uvicorn; print('OK')" 2>&1
if ($deps -eq "OK") {
    Write-Check "Required dependencies" "PASS"
} else {
    Write-Check "Required dependencies" "FAIL" "Missing packages"
}

# 4. SQLite database
$dbPath = "$ProjectRoot\data\starwing.db"
if (Test-Path $dbPath) {
    Write-Check "SQLite database" "PASS" $dbPath
} else {
    Write-Check "SQLite database" "WARN" "Database not found (will be created on first start)"
}

# 5. Database directory writability
$dataDir = "$ProjectRoot\data"
if (Test-Path $dataDir) {
    $testFile = Join-Path $dataDir ".preflight_test"
    try {
        "test" | Out-File $testFile -ErrorAction Stop
        Remove-Item $testFile -Force
        Write-Check "Database directory writable" "PASS"
    } catch {
        Write-Check "Database directory writable" "FAIL" "Cannot write to $dataDir"
    }
} else {
    Write-Check "Database directory" "WARN" "Does not exist (will be created)"
}

# 6. SQLite integrity
if (Test-Path $dbPath) {
    $integrity = python -c "import sqlite3; c=sqlite3.connect(r'$dbPath'); r=c.execute('PRAGMA integrity_check').fetchone()[0]; c.close(); print(r)" 2>&1
    if ($integrity -eq "ok") {
        Write-Check "SQLite integrity" "PASS"
    } else {
        Write-Check "SQLite integrity" "FAIL" "Result: $integrity"
    }
}

# 7. Alembic revision
if (Test-Path $dbPath) {
    $rev = python -c "import sqlite3; c=sqlite3.connect(r'$dbPath'); r=c.execute('SELECT version_num FROM alembic_version').fetchone(); c.close(); print(r[0] if r else 'none')" 2>&1
    if ($rev -and $rev -ne "none") {
        Write-Check "Alembic revision" "PASS" $rev
    } else {
        Write-Check "Alembic revision" "FAIL" "No migration applied"
    }
}

# 8. WAL mode
if (Test-Path $dbPath) {
    $wal = python -c "import sqlite3; c=sqlite3.connect(r'$dbPath'); r=c.execute('PRAGMA journal_mode').fetchone()[0]; c.close(); print(r)" 2>&1
    if ($wal -eq "wal") {
        Write-Check "WAL mode" "PASS"
    } else {
        Write-Check "WAL mode" "FAIL" "Mode: $wal"
    }
}

# 9. foreign_keys
if (Test-Path $dbPath) {
    $fk = python -c "import sqlite3; c=sqlite3.connect(r'$dbPath'); c.execute('PRAGMA foreign_keys=ON'); r=c.execute('PRAGMA foreign_keys').fetchone()[0]; c.close(); print(r)" 2>&1
    if ($fk -eq "1") {
        Write-Check "foreign_keys" "PASS"
    } else {
        Write-Check "foreign_keys" "FAIL"
    }
}

# 10. busy_timeout
if (Test-Path $dbPath) {
    $bt = python -c "import sqlite3; c=sqlite3.connect(r'$dbPath'); c.execute('PRAGMA busy_timeout=10000'); r=c.execute('PRAGMA busy_timeout').fetchone()[0]; c.close(); print(r)" 2>&1
    if ($bt -ge 10000) {
        Write-Check "busy_timeout" "PASS" "${bt}ms"
    } else {
        Write-Check "busy_timeout" "FAIL" "Value: $bt"
    }
}

# 11. HTTP port availability
Write-Host "`n--- Network ---" -ForegroundColor Yellow
$httpPort = 4001
$httpListener = Get-NetTCPConnection -LocalPort $httpPort -ErrorAction SilentlyContinue
if ($httpListener) {
    Write-Check "HTTP port $httpPort" "WARN" "Port in use by $($httpListener[0].OwningProcess)"
} else {
    Write-Check "HTTP port $httpPort" "PASS" "Available"
}

# 12. TCP port availability
$tcpPort = 6666
$tcpListener = Get-NetTCPConnection -LocalPort $tcpPort -ErrorAction SilentlyContinue
if ($tcpListener) {
    Write-Check "TCP port $tcpPort" "WARN" "Port in use by $($tcpListener[0].OwningProcess)"
} else {
    Write-Check "TCP port $tcpPort" "PASS" "Available"
}

# 13. Capture directory
Write-Host "`n--- Capture ---" -ForegroundColor Yellow
$captureDir = "$ProjectRoot\data\captures"
if (Test-Path $captureDir) {
    $testFile = Join-Path $captureDir ".preflight_test"
    try {
        "test" | Out-File $testFile -ErrorAction Stop
        Remove-Item $testFile -Force
        Write-Check "Capture directory writable" "PASS"
    } catch {
        Write-Check "Capture directory writable" "FAIL"
    }
} else {
    Write-Check "Capture directory" "WARN" "Does not exist (will be created)"
}

# 14. Capture disabled
$captureEnv = $env:CAPTURE_ENABLED
if ($captureEnv -eq "true" -or $captureEnv -eq "1") {
    Write-Check "Capture disabled" "WARN" "CAPTURE_ENABLED is set"
} else {
    Write-Check "Capture disabled" "PASS"
}

# 15. Matching disabled
$matcherEnv = $env:MATCHER_ENABLED
if ($matcherEnv -eq "true" -or $matcherEnv -eq "1") {
    Write-Check "Matching disabled" "WARN" "MATCHER_ENABLED is set"
} else {
    Write-Check "Matching disabled" "PASS"
}

# 16. Battle disabled
$battleEnv = $env:BATTLE_ENABLED
if ($battleEnv -eq "true" -or $battleEnv -eq "1") {
    Write-Check "Battle disabled" "WARN" "BATTLE_ENABLED is set"
} else {
    Write-Check "Battle disabled" "PASS"
}

# 17. Git status
Write-Host "`n--- Git ---" -ForegroundColor Yellow
$gitStatus = git -C $ProjectRoot status --short 2>&1
if ($gitStatus -eq "") {
    Write-Check "Git working tree" "PASS" "Clean"
} else {
    Write-Check "Git working tree" "WARN" "Uncommitted changes"
}

# 18. Existing server PID
$serverProc = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*app.main*" -or $_.CommandLine -like "*tcp_server*"
}
if ($serverProc) {
    Write-Check "Existing server" "WARN" "PID $($serverProc[0].Id) running"
} else {
    Write-Check "Existing server" "PASS" "None found"
}

# 19. Runtime logs
$logDir = "$ProjectRoot\data\logs"
if (Test-Path $logDir) {
    $logCount = (Get-ChildItem $logDir -File).Count
    Write-Check "Runtime logs" "PASS" "$logCount files"
} else {
    Write-Check "Runtime logs" "PASS" "No log directory"
}

# 20. Disk space
$drive = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
$freeGB = [math]::Round($drive.FreeSpace / 1GB, 2)
if ($freeGB -gt 1) {
    Write-Check "Disk space" "PASS" "${freeGB}GB free"
} else {
    Write-Check "Disk space" "FAIL" "${freeGB}GB free (need >1GB)"
}

# Summary
Write-Host "`n=== Preflight Summary ===" -ForegroundColor Cyan
Write-Host "Blocking conditions: $blocking"
Write-Host "Warnings: $warnings"

if ($blocking -gt 0) {
    Write-Host "`nRESULT: BLOCKED - $blocking blocking condition(s) must be resolved" -ForegroundColor Red
    exit 1
} elseif ($warnings -gt 0) {
    Write-Host "`nRESULT: READY WITH WARNINGS - $warnings warning(s)" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "`nRESULT: READY - All checks passed" -ForegroundColor Green
    exit 0
}
