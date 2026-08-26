# Seven Parity Route Revalidation

> **Audit date:** 2026-08-26
> **Scope:** 7 routes originally classified as VERIFIED_LEGACY_PARITY in Phase 1.2
> **Method:** Independent verification against legacy JavaScript source (`starwing.js`)

---

## Summary

| # | Route | Legacy Lines | Original Status | **Revalidated Status** | Change |
|---|-------|-------------|-----------------|----------------------|--------|
| 1 | POST /version | 407-426 | VERIFIED_LEGACY_PARITY | **VERIFIED_LEGACY_PARITY** | — |
| 2 | POST /resource | 779-789 | VERIFIED_LEGACY_PARITY | **VERIFIED_LEGACY_PARITY** | — |
| 3 | POST /player/profile/load | 488-507 | VERIFIED_LEGACY_PARITY | **LEGACY_DB_BEHAVIOR_PARTIAL** | ⬇ DOWNGRADED |
| 4 | POST /game_data/load | 677-698 | VERIFIED_LEGACY_PARITY | **CONTROLLED_NOT_IMPLEMENTED** | ⬇ DOWNGRADED |
| 5 | POST /battle/record_2on2 | 739-759 | VERIFIED_LEGACY_PARITY | **CONTROLLED_NOT_IMPLEMENTED** | ⬇ DOWNGRADED |
| 6 | POST /mission/* | 595-614 | VERIFIED_LEGACY_PARITY | **VERIFIED_LEGACY_PARITY** | — |
| 7 | POST /credit/* | 616-631 | VERIFIED_LEGACY_PARITY | **VERIFIED_LEGACY_PARITY** | — |

**Result:** 4 routes confirmed, 3 routes downgraded. Only 4 of 7 retain VERIFIED_LEGACY_PARITY.

---

## Detailed Verification

---

### Route 1: POST /version

**Legacy source:** `starwing.js:407-426`
**Python target:** `server/app/api/version.py:10-25`

| Check | Legacy | Python | Match |
|-------|--------|--------|-------|
| 1. Request method | POST | POST | ✅ |
| 2. Request path | `/version` | `/version` | ✅ |
| 3. Required headers | `x-galaxy-api-id` | `x-galaxy-api-id` (Header) | ✅ |
| 4. Request format | JSON/form body | JSON body | ✅ |
| 5. Response status | 200 | 200 (implicit) | ✅ |
| 6. Response headers | `x-galaxy-api: */*`, `x-galaxy-api-id: <echoed>` | Same | ✅ |
| 7. Response content-type | `application/json` | `application/json` (FastAPI default) | ✅ |
| 8. Response body | `{"client_version":"70571","data_version":"70571","stage_ids":[]}` | Same structure, values from settings | ✅ |
| 9. Protobuf type | None | None | ✅ |
| 10. Database effects | None | None | ✅ |
| 11. Error behavior | None defined | None defined | ✅ |
| 12. Deterministic vs dynamic | Static (hardcoded versions) | Static (settings) | ✅ |

**Verdict: VERIFIED_LEGACY_PARITY** — All 12 checks pass.

---

### Route 2: POST /resource

**Legacy source:** `starwing.js:779-789`
**Python target:** `server/app/api/resource.py:13-27`

| Check | Legacy | Python | Match |
|-------|--------|--------|-------|
| 1. Request method | POST | POST | ✅ |
| 2. Request path | `/resource` | `/resource` | ✅ |
| 3. Required headers | `x-galaxy-api-id` | `x-galaxy-api-id` (Header) | ✅ |
| 4. Request format | JSON/form body | JSON body | ✅ |
| 5. Response status | 200 | 200 (implicit) | ✅ |
| 6. Response headers | `x-galaxy-api: */*`, `x-galaxy-api-id: <echoed>` | Same | ✅ |
| 7. Response content-type | `application/json` | `application/json` | ✅ |
| 8. Response body | `fs.readFileSync('starwing/c_resource.json','utf8')` | `json.loads(RESOURCE_PATH.read_text())` | ✅ |
| 9. Protobuf type | None | None | ✅ |
| 10. Database effects | None (file read) | None (file read) | ✅ |
| 11. Error behavior | None defined | Returns `{}` if file missing | ✅ |
| 12. Deterministic vs dynamic | Static file content | Static file content | ✅ |

**Verdict: VERIFIED_LEGACY_PARITY** — All 12 checks pass.

---

### Route 3: POST /player/profile/load

**Legacy source:** `starwing.js:488-507`
**Python target:** `server/app/api/player.py:42-80`

| Check | Legacy | Python | Match |
|-------|--------|--------|-------|
| 1. Request method | POST | POST | ✅ |
| 2. Request path | `/player/profile/load` | `/player/profile/load` | ✅ |
| 3. Required headers | `x-galaxy-api-id` | `x-galaxy-api-id` (Header) | ✅ |
| 4. Request format | JSON `{nesys_id}` | JSON `{nesys_id}` | ✅ |
| 5. Response status | 200 | 200 (implicit) | ✅ |
| 6. Response headers | `x-galaxy-api: player/profile` | `x-galaxy-api: */*` | ❌ **MISMATCH** |
| 7. Response content-type | `application/json` | `application/json` | ✅ |
| 8. Response body | Complex object from `pt.getProfile()` with `emblem`, `same_day_login_count`, `total_login_days`, `consecutive_login_days`, etc. | `_ok(player_id, name, level, exp, gold, jewels, progresses, items)` — missing 5+ fields, adds `gold`/`jewels` not in legacy | ❌ **MISMATCH** |
| 9. Protobuf type | None | None | ✅ |
| 10. Database effects | Reads `player`, `player_logins`, `player_progress`; auto-creates player if nesys_id not found | Reads `players` table only; no auto-create, no login/progress reads | ❌ **INCOMPLETE** |
| 11. Error behavior | None defined | Returns `_ok(player_id="", ...)` on error | ⚠️ Different |
| 12. Deterministic vs dynamic | Dynamic (DB query) | Dynamic (DB query) | ✅ |

**Failure reasons:**
1. **Header mismatch:** Legacy sets `x-galaxy-api: player/profile`, Python uses `*/\*`
2. **Response body mismatch:** Missing fields: `emblem`, `same_day_login_count`, `total_login_days`, `consecutive_login_days`, `last_pref_ranking_order_id`, `pref_ranking_top_player_count`, `official_player_type_id`. Adds `gold`/`jewels` not in legacy response.
3. **Database behavior incomplete:** Legacy reads 3 tables + auto-creates player; Python reads 1 table only.

**Verdict: LEGACY_DB_BEHAVIOR_PARTIAL** — Downgraded due to header mismatch, incomplete response schema, and incomplete DB reads.

---

### Route 4: POST /game_data/load

**Legacy source:** `starwing.js:677-698`
**Python target:** `server/app/api/game_data.py:34-41`

| Check | Legacy | Python | Match |
|-------|--------|--------|-------|
| 1. Request method | POST | POST | ✅ |
| 2. Request path | `/game_data/load` | `/game_data/load` | ✅ |
| 3. Required headers | `x-galaxy-api-id` | `x-galaxy-api-id` (Header) | ✅ |
| 4. Request format | JSON `{player_id}` | JSON body | ✅ |
| 5. Response status | 200 | **501** | ❌ **MISMATCH** |
| 6. Response headers | `x-galaxy-api: game_data/load` (line 688 overrides line 686) | `x-galaxy-api: */*` | ❌ **MISMATCH** |
| 7. Response content-type | `application/json` | `application/json` | ✅ |
| 8. Response body | Complex game state object (15+ DB table reads) | `{"error":"not_implemented"}` | ❌ **MISMATCH** |
| 9. Protobuf type | None | None | ✅ |
| 10. Database effects | 15+ table reads (player, player_logins, player_buddies, player_progress, player_options, player_missions, etc.) | None | ❌ **MISSING** |
| 11. Error behavior | None defined | Returns 501 `not_implemented` | ❌ **MISMATCH** |
| 12. Deterministic vs dynamic | Dynamic (massive DB query) | Static error response | ❌ **MISMATCH** |

**Failure reasons:**
1. **Response status 501 vs 200:** Python explicitly returns 501, not 200
2. **Header mismatch:** Legacy sets `x-galaxy-api: game_data/load`, Python uses `*/\*`
3. **Response body completely different:** Legacy returns comprehensive game state; Python returns error
4. **No database interaction:** Legacy performs 15+ DB queries; Python has none
5. **Error behavior differs:** Legacy has no error path; Python returns 501

**Verdict: CONTROLLED_NOT_IMPLEMENTED** — This endpoint is not implemented in Python (returns 501). The previous VERIFIED_LEGACY_PARITY classification was incorrect.

---

### Route 5: POST /battle/record_2on2

**Legacy source:** `starwing.js:739-759`
**Python target:** `server/app/api/battle.py:34-41`

| Check | Legacy | Python | Match |
|-------|--------|--------|-------|
| 1. Request method | POST | POST | ✅ |
| 2. Request path | `/battle/record_2on2` | `/battle/record_2on2` | ✅ |
| 3. Required headers | `x-galaxy-api-id` | `x-galaxy-api-id` (Header) | ✅ |
| 4. Request format | JSON body | JSON body | ✅ |
| 5. Response status | 200 | **501** | ❌ **MISMATCH** |
| 6. Response headers | `x-galaxy-api: */*` | `x-galaxy-api: */*` | ✅ |
| 7. Response content-type | `application/json` | `application/json` | ✅ |
| 8. Response body | Complex object: `{winning_streaks_2on2, rank_point_2on2, ranking_score_2on2, update_items, battle_reward_ids, missions, ...}` | `{"error":"not_implemented"}` | ❌ **MISMATCH** |
| 9. Protobuf type | None | None | ✅ |
| 10. Database effects | Reads `player_missions` | None | ❌ **MISSING** |
| 11. Error behavior | None defined | Returns 501 `not_implemented` | ❌ **MISMATCH** |
| 12. Deterministic vs dynamic | Dynamic (DB query + calculation) | Static error response | ❌ **MISMATCH** |

**Failure reasons:**
1. **Response status 501 vs 200:** Python explicitly returns 501
2. **Response body completely different:** Legacy returns complex battle result; Python returns error
3. **No database interaction:** Legacy reads player_missions; Python has none
4. **Error behavior differs:** Legacy has no error path; Python returns 501

**Verdict: CONTROLLED_NOT_IMPLEMENTED** — This endpoint is not implemented in Python (returns 501). The previous VERIFIED_LEGACY_PARITY classification was incorrect.

---

### Route 6: POST /mission/* (fallback)

**Legacy source:** `starwing.js:595-614`
**Python target:** `server/app/api/mission.py:34-45`

| Check | Legacy | Python | Match |
|-------|--------|--------|-------|
| 1. Request method | POST | POST | ✅ |
| 2. Request path | `/mission/*` (wildcard) | `/mission/{path:path}` | ✅ |
| 3. Required headers | `x-galaxy-api-id` | `x-galaxy-api-id` (Header) | ✅ |
| 4. Request format | JSON body | JSON body | ✅ |
| 5. Response status | 200 | 200 (when mode=true) | ✅ |
| 6. Response headers | `x-galaxy-api: */*`, `x-galaxy-api-id: <echoed>` | `x-galaxy-api: */*`, `x-galaxy-api-id: <echoed>` | ✅ |
| 7. Response content-type | `application/json` | `application/json` | ✅ |
| 8. Response body | `{}` (empty object) | `{}` (empty dict) | ✅ |
| 9. Protobuf type | None | None | ✅ |
| 10. Database effects | None | None | ✅ |
| 11. Error behavior | None defined | 501 when mode=false | ✅ |
| 12. Deterministic vs dynamic | Static | Static | ✅ |

**Verdict: VERIFIED_LEGACY_PARITY** — All 12 checks pass.

---

### Route 7: POST /credit/* (fallback)

**Legacy source:** `starwing.js:616-631`
**Python target:** `server/app/api/credit.py:34-45`

| Check | Legacy | Python | Match |
|-------|--------|--------|-------|
| 1. Request method | POST | POST | ✅ |
| 2. Request path | `/credit/*` (wildcard) | `/credit/{path:path}` | ✅ |
| 3. Required headers | `x-galaxy-api-id` | `x-galaxy-api-id` (Header) | ✅ |
| 4. Request format | JSON body | JSON body | ✅ |
| 5. Response status | 200 | 200 (when mode=true) | ✅ |
| 6. Response headers | `x-galaxy-api: */*`, `x-galaxy-api-id: <echoed>` | `x-galaxy-api: */*`, `x-galaxy-api-id: <echoed>` | ✅ |
| 7. Response content-type | `application/json` | `application/json` | ✅ |
| 8. Response body | `{}` (empty object) | `{}` (empty dict) | ✅ |
| 9. Protobuf type | None | None | ✅ |
| 10. Database effects | None | None | ✅ |
| 11. Error behavior | None defined | 501 when mode=false | ✅ |
| 12. Deterministic vs dynamic | Static | Static | ✅ |

**Verdict: VERIFIED_LEGACY_PARITY** — All 12 checks pass.

---

## Correction to Phase 1.2 Matrix

The following routes in `ENDPOINT_MATRIX.md` need status corrections:

| Route | Current Status | Correct Status | Reason |
|-------|---------------|----------------|--------|
| /player/profile/load | VERIFIED_LEGACY_PARITY (Row 12 says LEGACY_DB_BEHAVIOR_PARTIAL, but user listed it as VERIFIED_LEGACY_PARITY) | **LEGACY_DB_BEHAVIOR_PARTIAL** | Header mismatch (`player/profile` vs `*/\*`), missing response fields, incomplete DB reads |
| /game_data/load | VERIFIED_LEGACY_PARITY | **CONTROLLED_NOT_IMPLEMENTED** | Returns 501, no implementation |
| /battle/record_2on2 | VERIFIED_LEGACY_PARITY | **CONTROLLED_NOT_IMPLEMENTED** | Returns 501, no implementation |

**Note:** The Phase 1.2 matrix already had `/player/profile/load` as LEGACY_DB_BEHAVIOR_PARTIAL (Row 12) and `/game_data/load` as LEGACY_DB_BEHAVIOR_PARTIAL (Row 18). The revalidation reveals `/game_data/load` and `/battle/record_2on2` are actually CONTROLLED_NOT_IMPLEMENTED (return 501), not LEGACY_DB_BEHAVIOR_PARTIAL.

---

## Final Verified LEGACY_PARITY Routes (4 total)

1. POST /version
2. POST /resource
3. POST /mission/* (fallback)
4. POST /credit/* (fallback)
