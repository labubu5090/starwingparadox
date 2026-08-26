# PostgreSQL Bootstrap Scripts

Safe PowerShell scripts for managing the Starwing Paradox test database.

## Safety Guarantees

- Default database: `starwing_test` (must end with `_test`)
- Refuses production-looking database names (`starwing`, `paradox`, names without `_test`)
- Never drops `postgres`, `template0`, `template1`
- Never drops unknown databases
- Passwords from environment variables or secure prompt
- Destructive operations require explicit `-Confirm` switch
- `$ErrorActionPreference = "Stop"` on all scripts
- Non-zero exit on failure

## Scripts

| Script | Purpose |
|--------|---------|
| `check-postgresql.ps1` | Verify PostgreSQL is available |
| `create-test-database.ps1` | Create `starwing_test` database and `starwing_test_user` |
| `import-legacy-schema.ps1` | Import `paradox.sql` into test database |
| `reset-test-database.ps1` | Destructive reset (requires `-Confirm`) |
| `verify-test-database.ps1` | Verify schema matches expected tables |
| `backup-test-database.ps1` | Backup before destructive operations |

## Quick Start

```powershell
# 1. Check PostgreSQL is available
.\check-postgresql.ps1

# 2. Create the test database
.\create-test-database.ps1

# 3. Import legacy schema
.\import-legacy-schema.ps1

# 4. Verify schema
.\verify-test-database.ps1

# 5. Reset (destructive - requires confirmation)
.\reset-test-database.ps1 -Confirm
```

## Environment Variables

Set these in `environment.ps1` (copy from `environment.example.ps1`):

```powershell
$PG_HOST = "localhost"
$PG_PORT = "5432"
$PG_USER = "starwing"
$PG_PASSWORD = "your_password"
$PG_DATABASE = "starwing_test"
$PG_SUPERUSER = "postgres"
```
