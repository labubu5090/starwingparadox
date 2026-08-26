# PostgreSQL Unavailability Notice

## Current Status

**PostgreSQL is NOT available** in the current development environment.

- Docker is not installed
- No native PostgreSQL installation detected
- `TEST_DATABASE_URL` environment variable is not set

## Impact on Tests

### Integration Tests

All integration tests are **skipped** when PostgreSQL is unavailable. This includes:

**Original integration tests** (`tests/integration/test_database_integration.py`):
- 22 tests skipped with message: "TEST_DATABASE_URL environment variable not set"

**New integration tests** (`tests/integration/test_player_integration.py`):
- 20 tests skipped with message: "TEST_DATABASE_URL environment variable not set"

### Test Suite Results

```
Total tests: 757
Passed: 710
Skipped: 42 (integration tests)
Failed: 5 (pre-existing issues, unrelated to database)
```

## How to Enable Integration Tests

### Option 1: Install PostgreSQL

1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Install with default settings
3. Create test database:
   ```sql
   CREATE DATABASE paradox_test;
   ```

### Option 2: Use Docker

1. Install Docker Desktop for Windows
2. Run:
   ```bash
   docker run -d --name starwing-postgres \
     -e POSTGRES_USER=paradox \
     -e POSTGRES_PASSWORD=changeme \
     -e POSTGRES_DB=paradox_test \
     -p 5432:5432 \
     postgres:16
   ```

### Option 3: Set Environment Variable

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://paradox:changeme@localhost:5432/paradox_test"
```

## Safety Measures

The test framework includes these safety measures:

1. **Database name must end with `_test`** - Prevents accidental writes to production
2. **Read-only snapshots** - Integration tests only read data
3. **Transaction rollback** - All test data is rolled back after each test
4. **Explicit skip** - Tests skip gracefully when PostgreSQL is unavailable

## Running Integration Tests

When PostgreSQL is available:

```bash
# Run all integration tests
python -m pytest tests/integration/ -ra --tb=short

# Run specific integration test
python -m pytest tests/integration/test_database_integration.py -ra --tb=short

# Run with verbose output
python -m pytest tests/integration/ -v
```

## Related Files

- `server/tests/integration/test_database_integration.py` - Original integration tests
- `server/tests/integration/test_player_integration.py` - Player-specific tests
- `server/app/database/compare.py` - Database comparison framework
- `server/tests/test_database_compare.py` - Comparison framework tests
- `docs/DATABASE_COMPARISON_GUIDE.md` - Comparison framework documentation
