<#
.SYNOPSIS
    Verify the test database schema matches expected tables.
.DESCRIPTION
    Checks that all expected tables exist in the test database.
    Returns non-zero exit code if any table is missing.
.PARAMETER Host
    PostgreSQL host (default: localhost)
#>
param(
    [string]$Host = "localhost",
    [string]$Port = "5432",
    [string]$User = "starwing_test_user"
)

$ErrorActionPreference = "Stop"

# Load environment if exists
$envFile = Join-Path $PSScriptRoot "environment.ps1"
if (Test-Path $envFile) {
    . $envFile
    if ($Host -eq "localhost" -and $PG_HOST) { $Host = $PG_HOST }
    if ($Port -eq "5432" -and $PG_PORT) { $Port = $PG_PORT }
    if ($User -eq "starwing_test_user" -and $PG_USER) { $User = $PG_USER }
}

$Database = "starwing_test"

# Safety: refuse non-test databases
if ($Database -notmatch "_test$") {
    Write-Error "Refusing to verify non-test database: $Database"
    exit 1
}

$expectedTables = @(
    "player",
    "player_buddies",
    "player_buddy_win_poses",
    "player_emblem_parts",
    "player_emblems",
    "player_line_colors",
    "player_logins",
    "player_mecha_colors",
    "player_mecha_set_parts",
    "player_mecha_sets",
    "player_missions",
    "player_options",
    "player_progress",
    "player_side_weapons",
    "player_titles",
    "player_weapon_set",
    "player_weapon_set_slots"
)

Write-Host "Verifying schema in '$Database'..." -ForegroundColor Cyan

# Get actual tables
$query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name;"
$actualTablesRaw = & psql -h $Host -p $Port -U $User -d $Database -t -A -c $query 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to query tables from '$Database'. Output: $actualTablesRaw"
    exit 1
}

$actualTables = $actualTablesRaw -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }

$missing = @()
foreach ($table in $expectedTables) {
    if ($table -notin $actualTables) {
        $missing += $table
    }
}

$extra = @()
foreach ($table in $actualTables) {
    if ($table -notin $expectedTables) {
        $extra += $table
    }
}

if ($missing.Count -gt 0) {
    Write-Host "`nMISSING TABLES:" -ForegroundColor Red
    foreach ($t in $missing) {
        Write-Host "  - $t" -ForegroundColor Red
    }
    Write-Error "Schema verification failed: $($missing.Count) table(s) missing"
    exit 1
}

if ($extra.Count -gt 0) {
    Write-Host "`nEXTRA TABLES (not in expected list):" -ForegroundColor Yellow
    foreach ($t in $extra) {
        Write-Host "  - $t" -ForegroundColor Yellow
    }
}

Write-Host "`nAll $($expectedTables.Count) expected tables found." -ForegroundColor Green
Write-Host "Schema verification passed." -ForegroundColor Green
exit 0
