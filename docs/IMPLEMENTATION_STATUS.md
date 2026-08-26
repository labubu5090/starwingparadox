# Implementation Status Model

> **Generated:** 2026-08-26
> **Baseline commit:** `ce7d30d`
> **Source:** `ENDPOINT_MATRIX.md` + `SEVEN_PARITY_ROUTE_REVALIDATION.md`

---

## Project Maturity Levels

| Level | Name | Description | Gate |
|-------|------|-------------|------|
| **0** | Source only | Legacy JS source exists; no Python implementation | Source file present |
| **1** | Python skeleton | Python route exists but returns stub/501; no real logic | Route registered, returns response |
| **2** | Source-derived regression parity | Response matches legacy source analysis; regression fixtures and tests exist | Fixture + test for route |
| **3** | Legacy runtime parity | Response matches legacy runtime behavior (observed, not just source-derived) | Legacy capture available |
| **4** | Real cabinet request replay | Captured real cabinet request/response replayed successfully | Capture evidence required |
| **5** | Single-cabinet functional validation | One real cabinet operates through full route lifecycle | Cabinet test pass |
| **6** | Multi-cabinet matching validation | Multiple cabinets produce consistent results | ≥2 cabinets tested |
| **7** | Full battle lifecycle validation | Complete battle flow (queue → match → fight → result) validated end-to-end | Full lifecycle capture |

**Rule:** No endpoint may be assigned LEVEL 4+ without real capture evidence.

---

## Route-by-Route Status

### Row 1: POST /version

| Field | Value |
|-------|-------|
| **Current status** | VERIFIED_LEGACY_PARITY |
| **Source evidence** | `starwing.js:407-426`, `version.py:10-25` |
| **Regression fixture count** | 1 (`legacy/http/version_check.json`) |
| **Regression test count** | 9 (test_version.py: 4, test_version_legacy.py: 13 overlapping) |
| **Database test status** | N/A (no DB) |
| **Capture requirement** | None (static response) |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | Yes |
| **Default enabled state** | Enabled |
| **Current level** | **2** |
| **Next required action** | None — verified via 12-point revalidation |

### Row 2: POST /resource

| Field | Value |
|-------|-------|
| **Current status** | VERIFIED_LEGACY_PARITY |
| **Source evidence** | `starwing.js:779-789`, `resource.py:13-27` |
| **Regression fixture count** | 1 (`legacy/http/resource_load.json`) |
| **Regression test count** | 5 (test_resource.py: 5, test_resource_legacy.py: 10 overlapping) |
| **Database test status** | N/A (file read) |
| **Capture requirement** | None (static file) |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | Yes |
| **Default enabled state** | Enabled |
| **Current level** | **2** |
| **Next required action** | None — verified via 12-point revalidation |

### Row 3: POST /matching/server

| Field | Value |
|-------|-------|
| **Current status** | LEGACY_STATIC_REIMPLEMENTED |
| **Source evidence** | `starwing.js:345-369`, `matching.py:34-43` |
| **Regression fixture count** | 0 (no legacy response fixture) |
| **Regression test count** | 13 (test_matching.py: 13, test_matching_legacy.py: 10) |
| **Database test status** | N/A (no DB) |
| **Capture requirement** | Real cabinet IP auth behavior needed |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No — response shape differs (`ip_addr` vs `servers[]`) |
| **Default enabled state** | Disabled (mode=true returns wrong shape) |
| **Current level** | **1** |
| **Next required action** | Fix response to return `{"ip_addr":"..."}`. Capture real cabinet request to verify IP auth side effect. |

### Row 4: POST /matching/match_id/generate

| Field | Value |
|-------|-------|
| **Current status** | LEGACY_STATIC_REIMPLEMENTED |
| **Source evidence** | `starwing.js:428-438`, `matching.py:46-55` |
| **Regression fixture count** | 0 |
| **Regression test count** | 13 (shared with matching suite) |
| **Database test status** | N/A (no DB) |
| **Capture requirement** | Real cabinet match_id format needed |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No — returns empty string instead of random int 10000-99999 |
| **Default enabled state** | Disabled |
| **Current level** | **1** |
| **Next required action** | Implement `random.randint(10000, 99999)`. Verify cabinet accepts integer match_id. |

### Row 5: POST /matching/* (fallback)

| Field | Value |
|-------|-------|
| **Current status** | LEGACY_STATIC_REIMPLEMENTED |
| **Source evidence** | `starwing.js:440-449` |
| **Regression fixture count** | 0 |
| **Regression test count** | 13 (shared with matching suite) |
| **Database test status** | N/A (no DB) |
| **Capture requirement** | None (empty object response) |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No — returns `{"result":1}` instead of `{}` |
| **Default enabled state** | Disabled |
| **Current level** | **1** |
| **Next required action** | Change response from `{"result":1}` to `{}`. |

### Row 6: POST /ranking/national

| Field | Value |
|-------|-------|
| **Current status** | LEGACY_STATIC_REIMPLEMENTED |
| **Source evidence** | `starwing.js:458-460`, `ranking.py` |
| **Regression fixture count** | 0 |
| **Regression test count** | 13 (test_ranking.py: 13) |
| **Database test status** | N/A (file read) |
| **Capture requirement** | Real ranking JSON file content needed |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No — returns empty array, no file read, wrong `x-galaxy-api` header |
| **Default enabled state** | Disabled |
| **Current level** | **1** |
| **Next required action** | Read `c_rankingNational.json`. Set `x-galaxy-api: ranking/national`. |

### Row 7: POST /ranking/location

| Field | Value |
|-------|-------|
| **Current status** | LEGACY_STATIC_REIMPLEMENTED |
| **Source evidence** | `starwing.js:462-464`, `ranking.py` |
| **Regression fixture count** | 0 |
| **Regression test count** | 13 (shared with ranking suite) |
| **Database test status** | N/A (file read) |
| **Capture requirement** | Real ranking JSON file content needed |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No — same gaps as /ranking/national |
| **Default enabled state** | Disabled |
| **Current level** | **1** |
| **Next required action** | Read `c_rankingStore.json`. Set `x-galaxy-api: ranking/location`. |

### Row 8: POST /ranking/prefecture

| Field | Value |
|-------|-------|
| **Current status** | LEGACY_STATIC_REIMPLEMENTED |
| **Source evidence** | `starwing.js:466-468`, `ranking.py` |
| **Regression fixture count** | 0 |
| **Regression test count** | 13 (shared with ranking suite) |
| **Database test status** | N/A (file read) |
| **Capture requirement** | Real ranking JSON file content needed |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No |
| **Default enabled state** | Disabled |
| **Current level** | **1** |
| **Next required action** | Read `c_rankingPrefecture.json`. Set `x-galaxy-api: ranking/prefecture`. |

### Row 9: POST /ranking/event

| Field | Value |
|-------|-------|
| **Current status** | LEGACY_STATIC_REIMPLEMENTED |
| **Source evidence** | `starwing.js:470-472`, `ranking.py` |
| **Regression fixture count** | 0 |
| **Regression test count** | 13 (shared with ranking suite) |
| **Database test status** | N/A (file read) |
| **Capture requirement** | Real ranking JSON file content needed |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No |
| **Default enabled state** | Disabled |
| **Current level** | **1** |
| **Next required action** | Read `c_rankingEvent.json`. Set `x-galaxy-api: ranking/event`. |

### Row 10: POST /ranking/weapon

| Field | Value |
|-------|-------|
| **Current status** | LEGACY_STATIC_REIMPLEMENTED |
| **Source evidence** | `starwing.js:474-479`, `ranking.py` |
| **Regression fixture count** | 0 |
| **Regression test count** | 13 (shared with ranking suite) |
| **Database test status** | N/A (file read) |
| **Capture requirement** | Real ranking JSON file content needed; role_id parameter behavior |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No — no file read, no `role_id` processing, wrong header |
| **Default enabled state** | Disabled |
| **Current level** | **1** |
| **Next required action** | Read `c_rankingWeapon_r{role_id}.json`. Inject `role_id`. Fix legacy header bug (`ranking/event` → `ranking/weapon`). |

### Row 11: POST /ranking/* (fallback)

| Field | Value |
|-------|-------|
| **Current status** | LEGACY_STATIC_REIMPLEMENTED |
| **Source evidence** | `starwing.js:481-485` |
| **Regression fixture count** | 0 |
| **Regression test count** | 13 (shared with ranking suite) |
| **Database test status** | N/A (no DB) |
| **Capture requirement** | None (empty object response) |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No — returns `{"result":1}` instead of `{}` |
| **Default enabled state** | Disabled |
| **Current level** | **1** |
| **Next required action** | Change response from `{"result":1}` to `{}`. |

### Row 12: POST /player/profile/load

| Field | Value |
|-------|-------|
| **Current status** | LEGACY_DB_BEHAVIOR_PARTIAL (downgraded from VERIFIED_LEGACY_PARITY) |
| **Source evidence** | `starwing.js:488-507`, `playerProfile.js:26-73`, `player.py:42-80` |
| **Regression fixture count** | 1 (`legacy/http/player_profile_load.json`) |
| **Regression test count** | 12 (test_player.py: 12, test_player_legacy.py: 8 overlapping) |
| **Database test status** | PARTIAL — reads `players` table only; legacy reads3 tables + auto-creates |
| **Capture requirement** | Real cabinet profile load request with nesys_id |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No — missing fields (`emblem`, `login_count`, etc.), wrong header, adds non-legacy fields |
| **Default enabled state** | Disabled |
| **Current level** | **1** |
| **Next required action** | Add missing response fields. Fix `x-galaxy-api` header to `player/profile`. Implement 3-table read + auto-create. Remove `gold`/`jewels` from response. |

### Row 13: POST /player/login

| Field | Value |
|-------|-------|
| **Current status** | LEGACY_DB_BEHAVIOR_PARTIAL |
| **Source evidence** | `starwing.js:509-531`, `playerProfile.js:351-392`, `player.py:79-108` |
| **Regression fixture count** | 0 |
| **Regression test count** | 12 (shared with player suite) |
| **Database test status** | PARTIAL — writes `player_logins`; legacy also reads `player`, `player_progress` |
| **Capture requirement** | Real cabinet login request |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No — missing `greeting_ids`, `battle_count`, `login_count` fields; wrong header |
| **Default enabled state** | Disabled |
| **Current level** | **1** |
| **Next required action** | Add missing response fields. Fix `x-galaxy-api` header to `player/login`. Implement full login state read. |

### Row 14: POST /player/login_bonus

| Field | Value |
|-------|-------|
| **Current status** | VERIFIED_LEGACY_PARITY (mode=true) |
| **Source evidence** | `starwing.js:534-554`, `player.py:110-121` |
| **Regression fixture count** | 0 |
| **Regression test count** | 39 (test_legacy_compat.py: 39) |
| **Database test status** | N/A (no DB in mode=true) |
| **Capture requirement** | None (static response in mode=true) |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | Yes (mode=true only) |
| **Default enabled state** | Enabled when mode=true |
| **Current level** | **2** |
| **Next required action** | None for mode=true. Legacy header is `player/login` not `*/\*` — cosmetic only. |

### Row 15: POST /player/register

| Field | Value |
|-------|-------|
| **Current status** | LEGACY_DB_BEHAVIOR_PARTIAL |
| **Source evidence** | `starwing.js:557-574`, `playerProfile.js:394-436`, `player.py:124-140` |
| **Regression fixture count** | 0 |
| **Regression test count** | 12 (shared with player suite) |
| **Database test status** | PARTIAL — UPDATE + UPSERT; response shape differs |
| **Capture requirement** | Real cabinet register request |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No — returns extra fields (`player_id`, `name`, `level`, etc.) instead of `{"result":1}` |
| **Default enabled state** | Disabled |
| **Current level** | **1** |
| **Next required action** | Strip response to `{"result":1}` only. Fix `x-galaxy-api` header to `player/register`. |

### Row 16: POST /player/* (fallback)

| Field | Value |
|-------|-------|
| **Current status** | VERIFIED_LEGACY_PARITY (mode=true) |
| **Source evidence** | `starwing.js:576-592` |
| **Regression fixture count** | 0 |
| **Regression test count** | 39 (shared with legacy compat suite) |
| **Database test status** | N/A (no DB) |
| **Capture requirement** | None |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | Yes (mode=true) |
| **Default enabled state** | Enabled when mode=true |
| **Current level** | **2** |
| **Next required action** | None |

### Row 17: POST /game_data/load/mission

| Field | Value |
|-------|-------|
| **Current status** | LEGACY_DB_BEHAVIOR_PARTIAL (revalidated as stub in mode=true) |
| **Source evidence** | `starwing.js:653-676`, `playerProfile.js:74-86`, `game_data.py` |
| **Regression fixture count** | 1 (`legacy/http/game_data_load_mission.json`) |
| **Regression test count** | 14 (test_game_data.py: 14, test_game_data_legacy.py: 12 overlapping) |
| **Database test status** | MISSING — legacy queries `player_missions`; Python returns empty array |
| **Capture requirement** | Real cabinet mission load request |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No — returns `{"result":1,"missions":[]}` with no DB query |
| **Default enabled state** | Disabled |
| **Current level** | **1** |
| **Next required action** | Implement `player_missions` query. Fix `x-galaxy-api` header to `game_data/load`. |

### Row 18: POST /game_data/load

| Field | Value |
|-------|-------|
| **Current status** | CONTROLLED_NOT_IMPLEMENTED (revalidated: returns 501) |
| **Source evidence** | `starwing.js:677-698`, `playerProfile.js:87-296`, `game_data.py:34-41` |
| **Regression fixture count** | 1 (`legacy/http/game_data_load.json`) |
| **Regression test count** | 14 (shared with game_data suite) |
| **Database test status** | MISSING — legacy performs 15+ DB table reads |
| **Capture requirement** | Real cabinet full game data load request |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No — returns 501, no implementation |
| **Default enabled state** | Disabled |
| **Current level** | **1** |
| **Next required action** | Implement 15+ table read logic from `playerProfile.js:87-296`. Largest gap in project. |

### Row 19: POST /game_data/save

| Field | Value |
|-------|-------|
| **Current status** | LEGACY_DB_BEHAVIOR_PARTIAL (mode=true stub) |
| **Source evidence** | `starwing.js:700-720`, `playerProfile.js:438-722`, `game_data.py` |
| **Regression fixture count** | 0 |
| **Regression test count** | 14 (shared with game_data suite) |
| **Database test status** | MISSING — legacy UPSERTs into 15+ tables |
| **Capture requirement** | Real cabinet save request with full game state |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No — returns `{"result":1}` with no DB writes, wrong response shape |
| **Default enabled state** | Disabled |
| **Current level** | **1** |
| **Next required action** | Implement UPSERT logic. Response must include `{result:1, missions:[...]}`. |

### Row 20: POST /game_data/* (fallback)

| Field | Value |
|-------|-------|
| **Current status** | VERIFIED_LEGACY_PARITY (mode=true) |
| **Source evidence** | `starwing.js:722-738` |
| **Regression fixture count** | 0 |
| **Regression test count** | 14 (shared with game_data suite) |
| **Database test status** | N/A (no DB) |
| **Capture requirement** | None |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | Yes (mode=true) |
| **Default enabled state** | Enabled when mode=true |
| **Current level** | **2** |
| **Next required action** | None |

### Row 21: POST /battle/record_2on2

| Field | Value |
|-------|-------|
| **Current status** | CONTROLLED_NOT_IMPLEMENTED (revalidated: returns 501) |
| **Source evidence** | `starwing.js:739-759`, `battleRecorder.js:1-47`, `battle.py:34-41` |
| **Regression fixture count** | 1 (`legacy/http/battle_record_2on2.json`) |
| **Regression test count** | 8 (test_battle.py: 8, test_battle_legacy.py: 10 overlapping) |
| **Database test status** | MISSING — legacy reads `player_missions` |
| **Capture requirement** | Real cabinet 2on2 battle result request |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | No — returns 501, no implementation |
| **Default enabled state** | Disabled |
| **Current level** | **1** |
| **Next required action** | Implement battle result response with `winning_streaks_2on2`, `rank_point_2on2`, `update_items`, `missions`, etc. |

### Row 22: POST /battle/* (fallback)

| Field | Value |
|-------|-------|
| **Current status** | VERIFIED_LEGACY_PARITY (mode=true) |
| **Source evidence** | `starwing.js:761-777` |
| **Regression fixture count** | 1 (`legacy/http/battle_fallback.json`) |
| **Regression test count** | 8 (shared with battle suite) |
| **Database test status** | N/A (no DB) |
| **Capture requirement** | None |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | Yes (mode=true) |
| **Default enabled state** | Enabled when mode=true |
| **Current level** | **2** |
| **Next required action** | None |

### Row 23: POST /mission/* (fallback)

| Field | Value |
|-------|-------|
| **Current status** | VERIFIED_LEGACY_PARITY |
| **Source evidence** | `starwing.js:595-614`, `mission.py:34-45` |
| **Regression fixture count** | 1 (`legacy/http/mission_fallback.json`) |
| **Regression test count** | 13 (test_matching.py includes mission paths) |
| **Database test status** | N/A (no DB) |
| **Capture requirement** | None |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | Yes |
| **Default enabled state** | Enabled |
| **Current level** | **2** |
| **Next required action** | None — verified via 12-point revalidation |

### Row 24: POST /credit/* (fallback)

| Field | Value |
|-------|-------|
| **Current status** | VERIFIED_LEGACY_PARITY |
| **Source evidence** | `starwing.js:616-631`, `credit.py:34-45` |
| **Regression fixture count** | 1 (`legacy/http/credit_fallback.json`) |
| **Regression test count** | 6 (test_credit.py: 6) |
| **Database test status** | N/A (no DB) |
| **Capture requirement** | None |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | Yes |
| **Default enabled state** | Enabled |
| **Current level** | **2** |
| **Next required action** | None — verified via 12-point revalidation |

### Row 25: POST /tutorial/* (fallback)

| Field | Value |
|-------|-------|
| **Current status** | VERIFIED_LEGACY_PARITY (mode=true) |
| **Source evidence** | `starwing.js:634-650`, `tutorial.py` |
| **Regression fixture count** | 0 |
| **Regression test count** | 0 (no dedicated tutorial tests) |
| **Database test status** | N/A (no DB) |
| **Capture requirement** | None |
| **Real cabinet validation status** | NOT_TESTED |
| **Safe to enable** | Yes (mode=true) |
| **Default enabled state** | Enabled when mode=true |
| **Current level** | **2** |
| **Next required action** | Add regression tests for tutorial fallback. |

### Row 26: POST /mock/matching/server

| Field | Value |
|-------|-------|
| **Current status** | CONTROLLED_NOT_IMPLEMENTED |
| **Source evidence** | `starwing.js:371-387` |
| **Regression fixture count** | 0 |
| **Regression test count** | 0 |
| **Database test status** | N/A |
| **Capture requirement** | N/A (mock route, not real cabinet) |
| **Real cabinet validation status** | NOT_APPLICABLE |
| **Safe to enable** | N/A — deliberate omission |
| **Default enabled state** | Not implemented |
| **Current level** | **0** |
| **Next required action** | None — deliberate. Only needed for legacy dev tooling. |

### Row 27: POST /mock/* (fallback)

| Field | Value |
|-------|-------|
| **Current status** | CONTROLLED_NOT_IMPLEMENTED |
| **Source evidence** | `starwing.js:389-405` |
| **Regression fixture count** | 0 |
| **Regression test count** | 0 |
| **Database test status** | N/A |
| **Capture requirement** | N/A |
| **Real cabinet validation status** | NOT_APPLICABLE |
| **Safe to enable** | N/A — deliberate omission |
| **Default enabled state** | Not implemented |
| **Current level** | **0** |
| **Next required action** | None — deliberate. |

### Row 28: GET /health

| Field | Value |
|-------|-------|
| **Current status** | SYNTHETIC_FOUNDATION_ONLY |
| **Source evidence** | `health.py:11` |
| **Regression fixture count** | 0 |
| **Regression test count** | 4 (test_health.py: 4) |
| **Database test status** | N/A |
| **Capture requirement** | N/A (synthetic) |
| **Real cabinet validation status** | NOT_APPLICABLE |
| **Safe to enable** | Yes |
| **Default enabled state** | Enabled |
| **Current level** | **3** |
| **Next required action** | None — infrastructure endpoint. |

### Row 29: GET /ready

| Field | Value |
|-------|-------|
| **Current status** | SYNTHETIC_FOUNDATION_ONLY |
| **Source evidence** | `health.py:16` |
| **Regression fixture count** | 0 |
| **Regression test count** | 4 (shared with health suite) |
| **Database test status** | Tests DB connectivity |
| **Capture requirement** | N/A (synthetic) |
| **Real cabinet validation status** | NOT_APPLICABLE |
| **Safe to enable** | Yes |
| **Default enabled state** | Enabled |
| **Current level** | **3** |
| **Next required action** | None — infrastructure endpoint. |

---

## Level Distribution Summary

| Level | Endpoints | Count |
|-------|-----------|-------|
| **0** | /mock/matching/server, /mock/* | 2 |
| **1** | /matching/server, /matching/match_id/generate, /matching/*, /ranking/national, /ranking/location, /ranking/prefecture, /ranking/event, /ranking/weapon, /ranking/*, /player/profile/load, /player/login, /player/register, /game_data/load/mission, /game_data/load, /game_data/save, /battle/record_2on2 | 16 |
| **2** | /version, /resource, /player/login_bonus, /player/*, /game_data/*, /battle/*, /mission/*, /credit/*, /tutorial/* | 9 |
| **3** | /health, /ready | 2 |
| **4+** | (none — no real capture evidence exists) | 0 |
| **Total** | | **29** |

---

## Enabled/Disabled Summary

| State | Endpoints | Count |
|-------|-----------|-------|
| **Enabled** | /version, /resource, /mission/*, /credit/*, /health, /ready | 6 |
| **Enabled when mode=true** | /player/login_bonus, /player/*, /game_data/*, /battle/*, /tutorial/* | 5 groups |
| **Disabled** | /matching/server, /matching/match_id/generate, /matching/*, /ranking/*, /player/profile/load, /player/login, /player/register, /game_data/load/mission, /game_data/load, /game_data/save, /battle/record_2on2 | 16 |
| **Not implemented** | /mock/matching/server, /mock/* | 2 |

---

## Critical Path to Level 4

No endpoint can reach Level 4 without real cabinet capture. The minimum required captures:

1. **POST /version** — verify cabinet accepts version response
2. **POST /resource** — verify cabinet parses resource JSON
3. **POST /matching/server** — capture real IP auth behavior and response format
4. **POST /player/profile/load** — capture real nesys_id lookup and full response schema
5. **POST /player/login** — capture real login flow and state reads
6. **POST /game_data/load** — capture full game state response (15+ tables)
7. **POST /game_data/save** — capture save request body and UPSERT behavior
8. **POST /battle/record_2on2** — capture real battle result response

---

## Fixture Inventory

| Category | Count | Location |
|----------|-------|----------|
| Legacy HTTP fixtures | 18 | `server/tests/fixtures/legacy/http/` |
| Database fixtures | 1 | `server/tests/fixtures/database/` |
| Manifest | 1 | `server/tests/fixtures/legacy/manifest.json` |
| **Total fixture files** | **20** | |

### Legacy HTTP Fixtures by Route

| Route | Fixture file | Status |
|-------|-------------|--------|
| /version | `version_check.json` | Present |
| /resource | `resource_load.json` | Present |
| /player/profile/load | `player_profile_load.json` | Present |
| /game_data/load | `game_data_load.json` | Present |
| /game_data/load/mission | `game_data_load_mission.json` | Present |
| /battle/record_2on2 | `battle_record_2on2.json` | Present |
| /battle/* | `battle_fallback.json` | Present |
| /mission/* | `mission_fallback.json` | Present |
| /credit/* | `credit_fallback.json` | Present |
| /matching/* | (none) | **MISSING** |
| /ranking/* | (none) | **MISSING** |
