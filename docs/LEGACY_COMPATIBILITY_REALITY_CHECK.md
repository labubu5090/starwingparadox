# LEGACY_COMPATIBILITY_MODE Reality Check

**Date:** 2026-08-26

---

## Executive Summary

LEGACY_COMPATIBILITY_MODE is a boolean toggle (`true`/`false`, default `true` per `config.py:17`) that gates whether stub endpoints return mock success (`{"result":1}`) or HTTP 501. **It only affects endpoints that have no DB implementation.** Real endpoints (profile/load, login, register) always return DB-backed data regardless of mode.

The documentation in LEGACY_COMPATIBILITY_MODE.md is largely accurate but incomplete. This document provides a per-endpoint reality check with exact code evidence.

---

## Configuration

```python
# server/app/config.py:17
legacy_compatibility_mode: bool = True
```

- **Default**: `true` (safe for legacy clients)
- **Type**: `bool` (Pydantic parses `"true"`/`"false"`/`"1"`/`"0"`/`"yes"`/`"no"`)
- **Invalid values**: Pydantic will coerce; non-string values raise validation error

---

## Mode Behavior Summary

| Mode | Stub Endpoints | Real Endpoints |
|------|---------------|----------------|
| `true` | 200 + `{"result":1,...}` | DB-backed (always) |
| `false` | 501 + `{"error":"not_implemented",...}` | DB-backed (always) |
| absent (env var unset) | Uses default `true` | DB-backed (always) |

---

## Per-Endpoint Matrix

### 1. POST /player/profile/load

- **Python**: DB-backed, always active. Never gated by LEGACY_COMPATIBILITY_MODE.
- **Legacy JS**: DB-backed via `playerProfile.js:26-73` (`initWithNesys` → PostgreSQL query)
- **Legacy response**: Full player object with `player_id`, `name`, `level`, `exp`, `progresses`, `emblem`, login stats, etc.
- **Python response**: `_ok(player_id=..., name=..., level=..., exp=..., gold=..., jewels=..., progresses=[], items=[])`
- **Differences**: Python omits `emblem`, `same_day_login_count`, `total_login_days`, `consecutive_login_days`, `last_pref_ranking_order_id`, `pref_ranking_top_player_count`, `official_player_type_id`, `location_id`, etc. Python adds `gold`/`jewels` not in legacy.
- **LEGACY_COMPATIBILITY_MODE effect**: None.
- **Classification**: **LEGACY_DB_BEHAVIOR_PARTIAL** — correct schema family but incomplete field set.

### 2. POST /player/login

- **Python**: DB-backed, always active.
- **Legacy JS**: DB-backed via `playerProfile.js:351-392` (`playerLogin` → INSERT into `player_logins` + multiple queries)
- **Legacy response**: Full player data + `progresses[]`, `greeting_ids:[1]`, `battle_count:3`, login stats, `burst_match:false`, `open_boss_matches:[20001]`, `next_boss_matches:[20002]`
- **Python response**: `_ok(player_id=..., progresses=[], login_bonuses=[])`
- **Differences**: Python missing `greeting_ids`, `battle_count`, `same_day_login_count`, `total_login_days`, `consecutive_login_days`, `burst_match`, `open_boss_matches`, `next_boss_matches`. Python adds `login_bonuses` (not in legacy login response).
- **LEGACY_COMPATIBILITY_MODE effect**: None.
- **Classification**: **LEGACY_DB_BEHAVIOR_PARTIAL** — correct table access pattern, severely incomplete response.

### 3. POST /player/login_bonus

- **Legacy JS** (`starwing.js:534-554`):
  ```javascript
  res.send("{\n" +
      "\"result\": 1, " +
      "\"login_bonuses\": [],"+
      "\"update_items\": {}"+
      "}");
  ```
- **Python** (`player.py:110-121`):
  ```python
  if not settings.legacy_compatibility_mode:
      return _not_implemented("/player/login_bonus", headers)
  return JSONResponse(
      content={"result": 1, "login_bonuses": [], "update_items": {}}, headers=headers
  )
  ```
- **Mode=false**: 501 + `{"error":"not_implemented","endpoint":"/player/login_bonus","corrid":"..."}`
- **Mode=true**: 200 + `{"result":1,"login_bonuses":[],"update_items":{}}`
- **LEGACY_COMPATIBILITY_MODE effect**: Gated. Matches legacy when `true`.
- **Classification**: **VERIFIED_LEGACY_PARITY** (when mode=true)

### 4. POST /player/register

- **Python**: DB-backed, always active. INSERT with ON CONFLICT.
- **Legacy JS** (`starwing.js:557-574` + `playerProfile.js:394-436`): DB-backed via `pt.playerRegister(req.body)` → UPDATE player + UPSERT player_progress
- **Legacy response**: `{"result": 1}`
- **Python response**: `_ok(player_id="", name=..., level=1, exp=0, gold=0, jewels=0)`
- **Differences**: Legacy returns ONLY `{"result":1}`. Python returns extra fields.
- **LEGACY_COMPATIBILITY_MODE effect**: None.
- **Classification**: **LEGACY_DB_BEHAVIOR_PARTIAL** — does DB work but response differs from legacy.

### 5. POST /player/{path} (fallback)

- **Legacy JS** (`starwing.js:576-592`):
  ```javascript
  res.send("{\n" +
      "\"result\": 1" +
      "}");
  ```
- **Python** (`player.py:155-166`):
  ```python
  if not settings.legacy_compatibility_mode:
      return _not_implemented(f"/player/{path}", headers)
  return JSONResponse(content=_ok(), headers=headers)
  ```
- **Mode=false**: 501 + error
- **Mode=true**: 200 + `{"result": 1}`
- **Classification**: **VERIFIED_LEGACY_PARITY** (when mode=true)

### 6. POST /matching/server

- **Legacy JS** (`starwing.js:345-369`):
  ```javascript
  res.set('x-galaxy-api', '*/*');
  res.set('x-galaxy-api-id',req.header('x-galaxy-api-id'));
  res.send("{\n" +
      "\t\"ip_addr\": \"" + matcher + "\"\n" +
      "}");
  ```
  Legacy also auto-authorizes client IP into `authorizedClients[]`.
- **Python** (`matching.py:34-43`):
  ```python
  if not settings.legacy_compatibility_mode:
      return _not_implemented("/matching/server", headers)
  return JSONResponse(content=_ok(servers=[]), headers=headers)
  ```
- **Mode=true**: Returns `{"result":1,"servers":[]}` — **MISSING `ip_addr` field**
- **Legacy returns**: `{"ip_addr":"paradox.yourdomain.com:6666"}`
- **Python does NOT**: authorize client IP (no `x-galaxy-real-ip` processing)
- **Classification**: **LEGACY_STATIC_REIMPLEMENTED** — wrong response shape, missing side effect

### 7. POST /matching/match_id/generate

- **Legacy JS** (`starwing.js:428-438`):
  ```javascript
  let matchId = getRandomInt(10000,99999);
  res.send("{\"match_id\":"+matchId+"}");
  ```
- **Python** (`matching.py:46-55`):
  ```python
  return JSONResponse(content=_ok(match_id=""), headers=headers)
  ```
- **Mode=true**: `{"result":1,"match_id":""}` — **match_id is empty string, not random int**
- **Classification**: **LEGACY_STATIC_REIMPLEMENTED** — wrong match_id type/value

### 8. POST /matching/{path} (fallback)

- **Legacy JS** (`starwing.js:440-449`): `res.send("{}")`
- **Python** (`matching.py:58-69`): `return JSONResponse(content=_ok(), headers=headers)` → `{"result":1}`
- **Difference**: Legacy returns `{}` (empty), Python returns `{"result":1}`
- **Classification**: **LEGACY_STATIC_REIMPLEMENTED** — wrong response body

### 9. POST /ranking/national

- **Legacy JS** (`starwing.js:458-460`):
  ```javascript
  res.set('x-galaxy-api', 'ranking/national');
  res.send(fs.readFileSync('starwing/c_rankingNational.json','utf8'));
  ```
- **Python** (`ranking.py:34-43`):
  ```python
  return JSONResponse(content=_ok(ranking=[]), headers=headers)
  ```
- **Mode=true**: `{"result":1,"ranking":[]}` — **MISSING actual ranking data from JSON file**
- **Legacy header**: `x-galaxy-api: ranking/national` (not `*/*`)
- **Classification**: **LEGACY_STATIC_REIMPLEMENTED** — wrong response body, wrong header

### 10. POST /ranking/location

- **Legacy JS** (`starwing.js:462-464`): Reads `c_rankingStore.json`, sets `x-galaxy-api: ranking/location`
- **Python**: `{"result":1,"ranking":[]}`
- **Classification**: **LEGACY_STATIC_REIMPLEMENTED** — same issues as /ranking/national

### 11. POST /ranking/prefecture

- **Legacy JS** (`starwing.js:466-468`): Reads `c_rankingPrefecture.json`, sets `x-galaxy-api: ranking/prefecture`
- **Python**: `{"result":1,"ranking":[]}`
- **Classification**: **LEGACY_STATIC_REIMPLEMENTED**

### 12. POST /ranking/event

- **Legacy JS** (`starwing.js:470-472`): Reads `c_rankingEvent.json`, sets `x-galaxy-api: ranking/event`
- **Python**: `{"result":1,"ranking":[]}`
- **Classification**: **LEGACY_STATIC_REIMPLEMENTED**

### 13. POST /ranking/weapon

- **Legacy JS** (`starwing.js:474-479`):
  ```javascript
  res.set('x-galaxy-api', 'ranking/event');
  let jWeapons = JSON.parse(fs.readFileSync('starwing/c_rankingWeapon_r'+req.body.role_id+'.json','utf8'));
  jWeapons.role_id = req.body.role_id;
  res.send(JSON.stringify(jWeapons,null,4));
  ```
- **Python**: `{"result":1,"ranking":[]}`
- **Classification**: **LEGACY_STATIC_REIMPLEMENTED** — no file read, no role_id processing

### 14. POST /ranking/{path} (fallback)

- **Legacy JS** (`starwing.js:481-485`): `res.send("{}")` (note: typo `deafult` in JS, never matches)
- **Python**: `{"result":1}`
- **Classification**: **LEGACY_STATIC_REIMPLEMENTED** — wrong body

### 15. POST /game_data/load/mission

- **Legacy JS** (`starwing.js:653-676`):
  ```javascript
  res.set('x-galaxy-api', 'game_data/load');
  let pt = new pp.PlayerProfile();
  await pt.initWithPlayerID(pgdb,req.body.player_id);
  let pgd = await pt.playerLoadGameDataMissions();
  res.send(JSON.stringify(pgd,0,4));
  ```
  DB-backed via `playerProfile.js:74-86` → queries `player_missions`.
- **Python** (`game_data.py:46-55`):
  ```python
  return JSONResponse(content=_ok(missions=[]), headers=headers)
  ```
- **Mode=true**: `{"result":1,"missions":[]}` — **no DB query**
- **Classification**: **LEGACY_DB_BEHAVIOR_PARTIAL** (mode=true gives wrong shape, mode=false gives 501)

### 16. POST /game_data/load

- **Legacy JS** (`starwing.js:677-698` + `playerProfile.js:87-296`): Massive DB operation reading 15+ tables.
- **Python** (`game_data.py:34-43`):
  ```python
  return JSONResponse(content=_ok(game_data={}), headers=headers)
  ```
- **Mode=true**: `{"result":1,"game_data":{}}` — **no DB query, empty object**
- **Classification**: **LEGACY_DB_BEHAVIOR_PARTIAL** (mode=true gives wrong shape)

### 17. POST /game_data/save

- **Legacy JS** (`starwing.js:700-720` + `playerProfile.js:438-722`): Massive DB UPSERT operation across 15+ tables. Returns `{result:1, missions:[...]}`.
- **Python** (`game_data.py:58-67`): `{"result":1}`
- **Classification**: **LEGACY_DB_BEHAVIOR_PARTIAL** (mode=true gives wrong shape, no DB writes)

### 18. POST /game_data/{path} (fallback)

- **Legacy JS** (`starwing.js:722-738`): `"{\n\"result\": 1\n}"`
- **Python**: `{"result":1}`
- **Classification**: **VERIFIED_LEGACY_PARITY** (when mode=true)

### 19. POST /battle/record_2on2

- **Legacy JS** (`starwing.js:739-759` + `battleRecorder.js:1-47`):
  ```javascript
  let myBr = new br.BattleRecorder(pgdb);
  let response = await myBr.battleRecord2on2(req.body);
  res.send(JSON.stringify(response,0,4));
  ```
  BattleRecorder returns: `winning_streaks_2on2:1`, `rank_point_2on2:10000`, `ranking_score_2on2:500`, etc. + DB query for missions.
- **Python** (`battle.py:30-39`):
  ```python
  return JSONResponse(content={"result": 1}, headers=headers)
  ```
- **Mode=true**: `{"result":1}` — **completely wrong response shape**
- **Classification**: **LEGACY_DB_BEHAVIOR_PARTIAL** (mode=true gives wrong shape)

### 20. POST /battle/{path} (fallback)

- **Legacy JS** (`starwing.js:761-777`): `"{\n\"result\": 1\n}"`
- **Python**: `{"result":1}`
- **Classification**: **VERIFIED_LEGACY_PARITY** (when mode=true)

### 21. POST /version

- **Legacy JS** (`starwing.js:407-426`):
  ```javascript
  res.set('x-galaxy-api', '*/*');
  res.set('x-galaxy-api-id',req.header('x-galaxy-api-id'));
  res.send("{\n" +
      "\t\"client_version\": \"" + version_main + "\",\n" +
      "\t\"data_version\": \"" + version_data + "\",\n" +
      "\t\"stage_ids\": []"+
      "}");
  ```
- **Python** (`version.py:10-23`):
  ```python
  return {
      "client_version": str(settings.version_main),
      "data_version": str(settings.version_data),
      "stage_ids": [],
  }
  ```
- **Difference**: Legacy returns version as quoted string (`"70571"`), Python returns string via `str()` which is the same. Shape matches.
- **Classification**: **VERIFIED_LEGACY_PARITY**

### 22. POST /resource

- **Legacy JS** (`starwing.js:779-789`):
  ```javascript
  res.send(fs.readFileSync('starwing/c_resource.json','utf8'));
  ```
- **Python** (`resource.py:13-25`):
  ```python
  if RESOURCE_PATH.exists():
      return json.loads(RESOURCE_PATH.read_text(encoding="utf8"))
  return {}
  ```
- **Both**: Read JSON file from disk and return it.
- **Classification**: **VERIFIED_LEGACY_PARITY**

### 23. GET /health

- **No legacy equivalent**. Infrastructure-only endpoint.
- **Classification**: **SYNTHETIC_FOUNDATION_ONLY**

### 24. GET /ready

- **No legacy equivalent**. Infrastructure-only endpoint.
- **Classification**: **SYNTHETIC_FOUNDATION_ONLY**

### 25. POST /mission/* (fallback)

- **Legacy JS** (`starwing.js:595-614`): `res.send("{\n}")` → returns `{}`
- **Python** (`mission.py:30-41`): `return JSONResponse(content={}, headers=headers)` → returns `{}`
- **Both**: Return empty object `{}`.
- **LEGACY_COMPATIBILITY_MODE effect**: When `false` → 501. When `true` → `{}`
- **Classification**: **VERIFIED_LEGACY_PARITY** (when mode=true, body matches)

### 26. POST /credit/* (fallback)

- **Legacy JS** (`starwing.js:616-631`): `res.send("{\n}")` → returns `{}`
- **Python** (`credit.py:30-41`): `return JSONResponse(content={}, headers=headers)` → returns `{}`
- **Both**: Return empty object `{}`.
- **Classification**: **VERIFIED_LEGACY_PARITY** (when mode=true, body matches)

### 27. POST /tutorial/* (fallback)

- **Legacy JS** (`starwing.js:634-650`): `res.send("{\n\"result\": 1\n}")` → returns `{"result":1}`
- **Python** (`tutorial.py:30-41`): `return JSONResponse(content={"result": 1}, headers=headers)` → returns `{"result":1}`
- **Classification**: **VERIFIED_LEGACY_PARITY** (when mode=true)

### 28. POST /mock/matching/server

- **Legacy JS** (`starwing.js:371-387`): Returns `{"ip_addr":"paradox.yourdomain.com:6666"}`
- **Python**: **NOT IMPLEMENTED** — no `/mock` route exists.
- **Classification**: **CONTROLLED_NOT_IMPLEMENTED**

### 29. POST /mock/* (fallback)

- **Legacy JS** (`starwing.js:389-405`): Returns `{"ip_addr":"paradox.yourdomain.com:6666"}`
- **Python**: **NOT IMPLEMENTED**.
- **Classification**: **CONTROLLED_NOT_IMPLEMENTED**

---

## Header Evidence

### Headers set by legacy JS (all routes):

```javascript
res.set('Content-type','application/json');
res.set('x-galaxy-api', '*/*');                    // varies per route
res.set('x-galaxy-api-id', req.header('x-galaxy-api-id'));  // echoed
```

### Header exceptions in legacy JS:

| Route | `x-galaxy-api` value | Legacy code |
|-------|---------------------|-------------|
| /ranking/national | `ranking/national` | `starwing.js:459` |
| /ranking/location | `ranking/location` | `starwing.js:463` |
| /ranking/prefecture | `ranking/prefecture` | `starwing.js:467` |
| /ranking/event | `ranking/event` | `starwing.js:471` |
| /ranking/weapon | `ranking/event` (BUG) | `starwing.js:475` |
| /player/profile/load | `player/profile` | `starwing.js:498` |
| /player/login | `player/login` | `starwing.js:519` |
| /player/login_bonus | `player/login` | `starwing.js:544` |
| /player/register | `player/register` | `starwing.js:564` |
| /game_data/load/mission | `game_data/load` | `starwing.js:665` |
| /game_data/load | `game_data/load` | `starwing.js:688` |
| /game_data/save | `game_data/save` | `starwing.js:709` |
| All other routes | `*/*` | starwing.js |

### Python headers:

All Python endpoints set `x-galaxy-api: */*` unconditionally via `_galaxy_headers()`. The route-specific `x-galaxy-api` values from legacy are **NOT replicated**.

**Evidence**: `player.py:31-35`:
```python
def _galaxy_headers(x_galaxy_api_id: str) -> dict:
    headers = {"x-galaxy-api": "*/*"}
    if x_galaxy_api_id:
        headers["x-galaxy-api-id"] = x_galaxy_api_id
    return headers
```

Real endpoints (`profile/load`, `login`, `register`) also use `*/*` instead of route-specific values.

---

## Critical Bugs in Legacy JS

1. **`res.status(200).end()` after `res.send()`**: Every route in `starwing.js` sets status AFTER sending the body. Express ignores this — status is always 200 anyway, but the code is misleading.

2. **`deafult` typo** (`starwing.js:481`): The `ranking/*` handler has `deafult:` instead of `default:`. This means the default case never executes — unknown ranking paths fall through without setting `x-galaxy-api` or sending a body (Express may send empty 200).

3. **`/ranking/weapon` sets wrong header** (`starwing.js:475`): `res.set('x-galaxy-api', 'ranking/event')` — should be `ranking/weapon`.

---

## Summary: Compatibility Score

| Category | Count | Routes |
|----------|-------|--------|
| **VERIFIED_LEGACY_PARITY** | 7 | /version, /resource, /player/{fallback}, /game_data/{fallback}, /battle/{fallback}, /mission/*, /credit/*, /tutorial/* |
| **LEGACY_DB_BEHAVIOR_PARTIAL** | 6 | /player/profile/load, /player/login, /player/register, /game_data/load/mission, /game_data/load, /game_data/save, /battle/record_2on2 |
| **LEGACY_STATIC_REIMPLEMENTED** | 9 | /matching/server, /matching/match_id/generate, /matching/{fallback}, /ranking/national, /ranking/location, /ranking/prefecture, /ranking/event, /ranking/weapon, /ranking/{fallback} |
| **SYNTHETIC_FOUNDATION_ONLY** | 2 | /health, /ready |
| **CONTROLLED_NOT_IMPLEMENTED** | 2 | /mock/matching/server, /mock/* |

**Bottom line**: Only 7 routes achieve true legacy parity (and only when mode=true). The 9 "reimplemented" routes return wrong response shapes. The 7 DB-backed routes are partially correct but missing significant response fields.
