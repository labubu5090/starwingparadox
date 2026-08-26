# PostgreSQL Integration Test Plan

**Date:** 2026-08-26
**Project:** Starwing Paradox Python Server
**Source Schema:** legacy-js/paradox.sql (PostgreSQL 12.6 dump)

---

## 1. Overview

Integration tests validate that the Python server's database operations produce
the same results as the legacy JavaScript server. Tests run against a real
PostgreSQL instance using a dedicated test database.

---

## 2. Environment Configuration

### 2.1 TEST_DATABASE_URL Format

```
TEST_DATABASE_URL=postgresql+psycopg://paradox:changeme@localhost:5432/paradox_test
```

The URL must use the `postgresql+psycopg` scheme (or `postgresql+asyncpg` for
async tests). The database name **must** end with `_test` suffix.

### 2.2 Database Name Validation

```python
# Enforced in test setup
assert db_name.endswith("_test"), (
    f"Database name must end with '_test' suffix for safety. Got: {db_name}"
)
```

### 2.3 Production Database Protection

The integration test module validates the database name on every connection
attempt. If the name does not end with `_test`, the test is **skipped** with
a clear error message. Tests will never modify production data.

---

## 3. Test Requirements

### 3.1 Minimum Schema

The integration tests require the schema defined in:
`server/tests/fixtures/database/legacy_minimum_seed.sql`

This includes:
- `player` (core table)
- `player_buddies`
- `player_logins`
- `player_progress`
- `player_missions`
- `player_options`
- `player_titles`
- `player_line_colors`
- `player_emblems`
- `player_emblem_parts`
- `player_mecha_sets`
- `player_mecha_set_parts`
- `player_mecha_colors`
- `player_weapon_set`
- `player_weapon_set_slots`
- `player_side_weapons`
- `player_buddy_win_poses`

### 3.2 Minimum Seed Data

Two test players (10010, 10011) with minimal associated data, derived from
the legacy `paradox.sql` dump.

### 3.3 PostgreSQL Version

Tested against PostgreSQL 12.6+ (matching legacy dump version).

---

## 4. Transaction Strategy

### 4.1 Rollback-Controlled Transactions

Each test function runs inside a transaction that is **rolled back** at the end:

```python
@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
```

This ensures:
- No test data persists between tests
- Tests can safely INSERT/UPDATE/DELETE
- No manual cleanup required

### 4.2 Test Isolation

Each test sees only the seed data (from `legacy_minimum_seed.sql`) plus any
rows it creates within its own transaction. Previous test writes are invisible.

---

## 5. Skip Behavior

Tests skip with a clear reason when PostgreSQL is unavailable:

```python
@pytest.fixture(scope="session")
def db_available():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set")
    if not url.endswith("_test") and "_test" not in url:
        pytest.skip("Database name must end with _test suffix")
    # Attempt connection
    try:
        engine = create_engine(url)
        engine.connect()
    except Exception as e:
        pytest.skip(f"PostgreSQL unavailable: {e}")
```

---

## 6. Test Categories

### 6.1 Connectivity Tests
- Verify TEST_DATABASE_URL is set
- Verify database name ends with `_test`
- Verify connection succeeds
- Verify schema exists

### 6.2 CRUD Tests
- Player creation (INSERT)
- Player lookup by nesys_id
- Player lookup by player_id
- Player update (UPSERT patterns)

### 6.3 Legacy SQL Quirk Tests
- `ON CONFLICT ... DO UPDATE` (UPSERT) for player_progress, player_buddies
- `date_trunc('day', ts_when)` for login counting
- `COUNT(DISTINCT(date_trunc(...)))` for total_login_days

### 6.4 Route Integration Tests (Phase 2)
- POST /player/profile/load against real DB
- POST /player/login against real DB
- POST /game_data/load against real DB
- POST /game_data/save against real DB

---

## 7. Running Integration Tests

```bash
# Set the test database URL
export TEST_DATABASE_URL="postgresql+psycopg://paradox:changeme@localhost:5432/paradox_test"

# Create the test database
createdb paradox_test

# Load minimum schema
psql paradox_test < server/tests/fixtures/database/legacy_minimum_seed.sql

# Run integration tests
pytest server/tests/integration/ -v

# Run only integration tests (skip unit tests)
pytest server/tests/integration/ -v -m integration
```

---

## 8. Legacy Route → Database Table Mapping

| Route | Tables Read | Tables Written | Legacy Source |
|-------|------------|----------------|---------------|
| POST /player/profile/load | player, player_logins, player_progress | — | starwing.js:488-507 |
| POST /player/login | player, player_logins, player_progress | player_logins | starwing.js:509-531 |
| POST /player/register | player | player, player_progress | starwing.js:557-574 |
| POST /game_data/load | player, player_logins, player_buddies, player_progress, player_options, player_missions, player_buddy_win_poses, player_emblems, player_emblem_parts, player_titles, player_line_colors, player_mecha_sets, player_mecha_set_parts, player_mecha_colors, player_weapon_set, player_weapon_set_slots, player_side_weapons | — | starwing.js:677-698 |
| POST /game_data/load/mission | player_missions | — | starwing.js:653-676 |
| POST /game_data/save | player, player_options, player_buddies, player_progress, player_missions, player_titles, player_emblems, player_emblem_parts, player_mecha_sets, player_mecha_set_parts, player_buddy_win_poses, player_line_colors, player_mecha_colors, player_weapon_set, player_weapon_set_slots, player_side_weapons | All above | starwing.js:700-720, playerProfile.js:438-722 |

---

## 9. Legacy SQL Quirks

1. **UPSERT patterns everywhere**: Most save operations use `ON CONFLICT ... DO UPDATE`
   rather than separate INSERT/UPDATE. The Python reimplementation must match this
   behavior for data consistency.

2. **date_trunc for login counting**: `date_trunc('day', ts_when)` extracts the
   date portion for same-day login counting. This is PostgreSQL-specific.

3. **INET type for IP addresses**: `ip_addr` column uses PostgreSQL `INET` type,
   not `VARCHAR`. This affects parameterized queries.

4. **player_id sequence**: The `player.player_id` column uses a PostgreSQL sequence
   (`player_player_id_seq`). New players get auto-assigned IDs.

5. **No foreign key constraints**: The legacy schema has no `REFERENCES` clauses.
   Referential integrity is enforced at the application level.

6. **CASCADE behavior**: Not present in legacy schema. Deleting a player does not
   automatically clean up related rows.
