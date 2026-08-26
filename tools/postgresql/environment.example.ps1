# Starwing Paradox - PostgreSQL Environment Variables (Example)
# Copy this file to environment.ps1 and set your values.
# Never commit environment.ps1 to version control.

$PG_HOST = "localhost"
$PG_PORT = "5432"
$PG_USER = "starwing"
$PG_PASSWORD = ""  # Set via secure prompt or environment variable
$PG_DATABASE = "starwing_test"
$PG_SUPERUSER = "postgres"

# Legacy schema file
$LEGACY_SCHEMA = Join-Path $PSScriptRoot "..\..\legacy-js\paradox.sql"
