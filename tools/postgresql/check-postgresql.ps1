<#
.SYNOPSIS
    Check if PostgreSQL is available and reachable.
.DESCRIPTION
    Verifies psql is installed, PostgreSQL service is running, and connection works.
    Exits with non-zero code on failure.
.PARAMETER Host
    PostgreSQL host (default: localhost)
.PARAMETER Port
    PostgreSQL port (default: 5432)
#>
param(
    [string]$Host = "localhost",
    [string]$Port = "5432"
)

$ErrorActionPreference = "Stop"

Write-Host "Checking PostgreSQL availability..." -ForegroundColor Cyan

# Load environment if exists
$envFile = Join-Path $PSScriptRoot "environment.ps1"
if (Test-Path $envFile) {
    . $envFile
    if ($Host -eq "localhost" -and $PG_HOST) { $Host = $PG_HOST }
    if ($Port -eq "5432" -and $PG_PORT) { $Port = $PG_PORT }
}

# Check psql is available
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psqlPath) {
    Write-Error "psql not found in PATH. Is PostgreSQL installed?"
    exit 1
}
Write-Host "  [OK] psql found: $($psqlPath.Source)" -ForegroundColor Green

# Check pg_isready
$pgReady = & pg_isready -h $Host -p $Port 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "PostgreSQL is not ready at ${Host}:${Port}. Output: $pgReady"
    exit 1
}
Write-Host "  [OK] PostgreSQL is ready at ${Host}:${Port}" -ForegroundColor Green

# Check connection with SELECT 1
$testQuery = "SELECT 1 AS alive;"
$result = & psql -h $Host -p $Port -U postgres -t -A -c $testQuery 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Connection test failed with postgres user. Trying default user..."
    $result = & psql -h $Host -p $Port -t -A -c $testQuery 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Cannot connect to PostgreSQL at ${Host}:${Port}. Output: $result"
        exit 1
    }
}
Write-Host "  [OK] Connection test passed" -ForegroundColor Green
Write-Host "PostgreSQL is available." -ForegroundColor Cyan
exit 0
