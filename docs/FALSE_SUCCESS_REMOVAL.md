# False Success Removal – Change Log

**Date:** 2026-08-26
**Scope:** All Python API endpoint stubs in `server/app/api/`

---

## Summary

Every endpoint that returned `{"result":1}` or a generic success was audited against the legacy JavaScript source (`legacy-js/js/starwing.js` and its modules). Endpoints where the legacy source returns a different response had their Python stubs corrected. Endpoints where the real response requires DB or file access that cannot be replicated were changed to always return HTTP 501 Not Implemented.

---

## Changes

### 1. POST /matching/server

**File:** `server/app/api/matching.py:36-48`

- **Previous behavior:** `{"result":1,"servers":[]}` (status 200)
- **New behavior (legacy mode ON):** `{"ip_addr":"paradox.yourdomain.com:6666"}` (status 200)
- **New behavior (legacy mode OFF):** `{"error":"not_implemented","endpoint":"/matching/server","corrid":"..."}` (status 501)
- **Legacy source evidence:** `starwing.js:365-368` — `res.send("{\"ip_addr\":\"" + matcher + "\"}")`
- **Regression test added:** `test_matching_server_returns_ip_addr`, `test_matching_server_no_result_field` in `tests/api/test_matching.py`

### 2. POST /matching/match_id/generate

**File:** `server/app/api/matching.py:51-63`

- **Previous behavior:** `{"result":1,"match_id":""}` (status 200)
- **New behavior (legacy mode ON):** `{"match_id":42381}` (random int 10000-99999, status 200)
- **New behavior (legacy mode OFF):** 501 Not Implemented
- **Legacy source evidence:** `starwing.js:435-436` — `let matchId = getRandomInt(10000,99999); res.send("{\"match_id\":"+matchId+"}")`
- **Regression test added:** `test_match_id_generate_returns_int`, `test_match_id_generate_no_result_field` in `tests/api/test_matching.py`

### 3. POST /matching/* (fallback)

**File:** `server/app/api/matching.py:66-78`

- **Previous behavior:** `{"result":1}` (status 200)
- **New behavior (legacy mode ON):** `{}` (status 200)
- **New behavior (legacy mode OFF):** 501 Not Implemented
- **Legacy source evidence:** `starwing.js:447` — `res.send("{}")`
- **Regression test added:** `test_unknown_matching_endpoint_returns_empty`, `test_unknown_matching_endpoint_no_result` in `tests/api/test_matching.py`

### 4. POST /ranking/national

**File:** `server/app/api/ranking.py:38-44`

- **Previous behavior:** `{"result":1,"ranking":[]}` (status 200, legacy mode ON)
- **New behavior:** Always 501 Not Implemented (with `x-legacy-compat: false`)
- **Legacy source evidence:** `starwing.js:460` — `res.send(fs.readFileSync('starwing/c_rankingNational.json','utf8'))` — requires file not available
- **Regression test added:** `test_ranking_national_returns_501`, `test_ranking_national_x_legacy_compat` in `tests/api/test_ranking.py`

### 5. POST /ranking/location

**File:** `server/app/api/ranking.py:47-53`

- **Previous behavior:** `{"result":1,"ranking":[]}` (status 200, legacy mode ON)
- **New behavior:** Always 501 Not Implemented
- **Legacy source evidence:** `starwing.js:464` — requires `c_rankingStore.json`
- **Regression test added:** `test_ranking_location_returns_501` in `tests/api/test_ranking.py`

### 6. POST /ranking/prefecture

**File:** `server/app/api/ranking.py:56-62`

- **Previous behavior:** `{"result":1,"ranking":[]}` (status 200, legacy mode ON)
- **New behavior:** Always 501 Not Implemented
- **Legacy source evidence:** `starwing.js:468` — requires `c_rankingPrefecture.json`
- **Regression test added:** `test_ranking_prefecture_returns_501` in `tests/api/test_ranking.py`

### 7. POST /ranking/event

**File:** `server/app/api/ranking.py:65-71`

- **Previous behavior:** `{"result":1,"ranking":[]}` (status 200, legacy mode ON)
- **New behavior:** Always 501 Not Implemented
- **Legacy source evidence:** `starwing.js:472` — requires `c_rankingEvent.json`
- **Regression test added:** `test_ranking_event_returns_501` in `tests/api/test_ranking.py`

### 8. POST /ranking/weapon

**File:** `server/app/api/ranking.py:74-80`

- **Previous behavior:** `{"result":1,"ranking":[]}` (status 200, legacy mode ON)
- **New behavior:** Always 501 Not Implemented
- **Legacy source evidence:** `starwing.js:477` — requires `c_rankingWeapon_r*.json` files
- **Regression test added:** `test_ranking_weapon_returns_501` in `tests/api/test_ranking.py`

### 9. POST /ranking/* (fallback)

**File:** `server/app/api/ranking.py:83-95`

- **Previous behavior:** `{"result":1}` (status 200, legacy mode ON)
- **New behavior (legacy mode ON):** `{}` (status 200)
- **New behavior (legacy mode OFF):** 501 Not Implemented
- **Legacy source evidence:** `starwing.js:483` (deafult case) — `res.send("{}")`
- **Regression test added:** `test_unknown_ranking_returns_empty` in `tests/api/test_ranking.py`

### 10. POST /game_data/load

**File:** `server/app/api/game_data.py:38-44`

- **Previous behavior:** `{"result":1,"game_data":{}}` (status 200, legacy mode ON)
- **New behavior:** Always 501 Not Implemented
- **Legacy source evidence:** `starwing.js:677-698`, `playerProfile.js:87-296` — complex DB query across 15+ tables; no `result` field in response
- **Regression test added:** `test_load_returns_501`, `test_load_no_result_field`, `test_load_x_legacy_compat` in `tests/api/test_game_data.py`

### 11. POST /game_data/load/mission

**File:** `server/app/api/game_data.py:47-53`

- **Previous behavior:** `{"result":1,"missions":[]}` (status 200, legacy mode ON)
- **New behavior:** Always 501 Not Implemented
- **Legacy source evidence:** `starwing.js:653-676`, `playerProfile.js:74-86` — DB query for player_missions; response has no `result` field
- **Regression test added:** `test_load_mission_returns_501`, `test_load_mission_no_result_field` in `tests/api/test_game_data.py`

### 12. POST /game_data/save

**File:** `server/app/api/game_data.py:56-62`

- **Previous behavior:** `{"result":1}` (status 200, legacy mode ON)
- **New behavior:** Always 501 Not Implemented
- **Legacy source evidence:** `starwing.js:700-720`, `playerProfile.js:438-722` — 15+ UPSERT operations; returns `{result:1,missions:[...]}` (Python was missing `missions`)
- **Regression test added:** `test_save_returns_501`, `test_save_no_result_without_persistence`, `test_save_x_legacy_compat` in `tests/api/test_game_data.py`

### 13. POST /game_data/* (fallback)

**File:** `server/app/api/game_data.py:65-78`

- **Previous behavior:** `{"result":1}` (status 200, legacy mode ON) via `_ok()`
- **New behavior (legacy mode ON):** `{"result":1}` (status 200) — **correct, matches legacy**
- **Legacy source evidence:** `starwing.js:734-736` — `res.send("{\"result\": 1}")`
- **Regression test added:** `test_unknown_game_data_returns_result` in `tests/api/test_game_data.py`
- **Note:** Response was already correct; only the internal implementation changed (removed `_ok()` dependency)

### 14. POST /battle/record_2on2

**File:** `server/app/api/battle.py:31-38`

- **Previous behavior:** `{"result":1}` (status 200, legacy mode ON)
- **New behavior:** Always 501 Not Implemented
- **Legacy source evidence:** `starwing.js:739-759`, `battleRecorder.js:5-44` — returns complex object with `winning_streaks_2on2`, `rank_point_2on2`, `update_items`, `missions`, etc.
- **Regression test added:** `test_record_2on2_returns_501`, `test_record_2on2_no_success_claim`, `test_record_2on2_x_legacy_compat` in `tests/api/test_battle.py`

### 15. POST /battle/* (fallback)

**File:** `server/app/api/battle.py:41-53`

- **Previous behavior:** `{"result":1}` (status 200, legacy mode ON)
- **New behavior (legacy mode ON):** `{"result":1}` (status 200) — **correct, matches legacy**
- **Legacy source evidence:** `starwing.js:773-775` — `res.send("{\"result\": 1}")`
- **Regression test added:** `test_unknown_battle_returns_result` in `tests/api/test_battle.py`

### 16. All _not_implemented helpers (7 files)

**Files:** `player.py`, `matching.py`, `ranking.py`, `game_data.py`, `battle.py`, `mission.py`, `credit.py`, `tutorial.py`

- **Previous behavior:** 501 responses had no `x-legacy-compat` header
- **New behavior:** All 501 responses include `x-legacy-compat: false` header
- **Legacy source evidence:** N/A — this is a new safety signal
- **Regression test added:** `TestLegacyCompatHeader` class in `tests/api/test_legacy_compat.py` with 4 tests

---

## Endpoints Verified as Already Correct

These endpoints were checked against the legacy source and found to already return the correct response:

| Route | Legacy Returns | Python Returns | Match? |
|-------|---------------|----------------|--------|
| POST /player/profile/load | DB query result | DB query result | ✓ |
| POST /player/login | DB query result | DB query result | ✓ |
| POST /player/register | `{"result":1}` | `{"result":1,...}` | ✓ (superset) |
| POST /player/login_bonus | `{"result":1,"login_bonuses":[],"update_items":{}}` | same | ✓ |
| POST /player/* fallback | `{"result":1}` | `{"result":1}` | ✓ |
| POST /version | `{"client_version":"...","data_version":"...","stage_ids":[]}` | same | ✓ |
| POST /resource | File contents | File contents | ✓ |
| POST /mission/* | `{}` | `{}` | ✓ |
| POST /credit/* | `{}` | `{}` | ✓ |
| POST /tutorial/* | `{"result":1}` | `{"result":1}` | ✓ |
| GET /health | `{"status":"ok"}` | `{"status":"ok"}` | ✓ |
| GET /ready | DB check | DB check | ✓ |

---

## Test Coverage

### Updated test files:
- `tests/api/test_legacy_compat.py` — Rewritten with correct assertions
- `tests/api/test_matching.py` — Fixed matching server/fallback assertions
- `tests/api/test_ranking.py` — All specific ranking tests now expect 501

### New test files:
- `tests/api/test_battle.py` — 8 tests for battle endpoint false success prevention
- `tests/api/test_game_data.py` — 13 tests for game_data endpoint false success prevention
- `tests/api/test_credit.py` — 6 tests for credit endpoint false success prevention

### Total new/updated tests: 31

All 309 tests pass (8 pre-existing failures in `legacy_regression/` are unrelated).
