# ADR-001: SQLite-Only Architecture

## Decision

The Starwing Paradox Python server will use SQLite as its only supported runtime database.

## Date

2026-08-27

## Context

The project originally used PostgreSQL for development and testing. After completing PostgreSQL validation (commit `405ddaf`), the decision was made to simplify the deployment model to SQLite-only.

Key factors:
- Single-cabinet deployment model (one server process, one local database)
- No need for multi-process database access
- No need for network database connections
- Simpler installation and operation
- No external database service dependency

## Decision

SQLite is the only supported database backend. PostgreSQL is removed as a runtime, development, deployment, and testing requirement.

## Alternatives Rejected

1. **Dual-backend (PostgreSQL + SQLite)**: Rejected because it adds complexity without benefit for the single-cabinet deployment model.

2. **PostgreSQL-only**: Rejected because it requires an external database service, complicating single-cabinet deployment.

3. **MySQL/MSSQL**: Rejected because they add external dependencies without benefit.

## Consequences

### Positive
- Zero external database dependencies
- Simple installation (Python packages only)
- Single-file database
- WAL mode for concurrent reads
- Built-in backup via SQLite backup API
- Atomic file-level backups

### Negative
- Single writer process only (no multi-server support)
- No network database access
- Concurrency limited to WAL mode capabilities
- Cannot share database across multiple servers

## Supported Deployment Scale

- One Starwing server process
- Multiple HTTP and TCP connections
- One local SQLite database
- Local filesystem only

## Concurrency Limits

- Multiple concurrent readers allowed (WAL mode)
- Sequential writes (one writer at a time)
- busy_timeout configured to 10 seconds
- No support for multiple independent writer processes
- No support for network-share database files

## Revisit Conditions

This ADR should be revisited if any of the following occur:
1. Multiple independent server processes need to write to the same database
2. Sustained SQLITE_BUSY errors under production load
3. Multi-cabinet write contention
4. Distributed matching requiring shared state
5. Battle coordination requiring shared state

## References

- SQLite WAL mode: https://www.sqlite.org/wal.html
- SQLite backup API: https://www.sqlite.org/backup.html
- PostgreSQL validation commit: `405ddaf`
