# PostgreSQL Tools (ARCHIVED)

These PostgreSQL tools are **no longer supported** as of the SQLite-only migration.

## Status

- **SQLite is the only active database backend**
- These tools must not be used for current deployment
- PostgreSQL validation commit `405ddaf` remains in Git history

## Tools Archived

- `check-postgresql.ps1` - PostgreSQL availability check
- `create-test-database.ps1` - Test DB creation
- `import-legacy-schema.ps1` - Legacy schema import
- `reset-test-database.ps1` - Test DB reset
- `verify-test-database.ps1` - Schema verification
- `backup-test-database.ps1` - Test DB backup
- `environment.example.ps1` - Environment template
- `README.md` - PostgreSQL tools documentation

## Migration

The project migrated from PostgreSQL to SQLite-only operation. See:
- `docs/ADR_001_SQLITE_ONLY.md` - Architecture Decision Record
- `docs/SQLITE_ONLY_MIGRATION_FINAL_REPORT.md` - Final migration report
