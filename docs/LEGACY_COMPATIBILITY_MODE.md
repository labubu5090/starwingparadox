# Legacy Compatibility Mode

**Date:** 2026-08-26

---

## Overview

The `LEGACY_COMPATIBILITY_MODE` environment variable controls whether legacy API stubs return mock success responses or proper HTTP 501 Not Implemented responses. It **only** affects stub endpoints that lack real DB implementations. DB-backed endpoints (profile/load, login, register, version, resource) always return real data regardless of this setting.

---

## Configuration

| Variable | Type | Default | Source |
|----------|------|---------|--------|
| `LEGACY_COMPATIBILITY_MODE` | `bool` | `true` | `server/appconfig.py:17` |

Set via `.env` file or environment variable. Pydantic parses `"true"/"false"/"1"/"0"/"yes"/"no"` (case-insensitive).

---

## Behavior

### `LEGACY_COMPATIBILITY_MODE=false` (Strict Mode)

- Stub endpoints return **HTTP 501 Not Implemented** with body:
  ```json
  {"error": "not_implemented", "endpoint": "/path", "corrid": "uuid"}
  ```
- All 501 responses include header `x-legacy-compat: false`
- Real endpoints function normally
- Recommended for development and new integrations

### `LEGACY_COMPATIBILITY_MODE=true` (Legacy Mode, DEFAULT)

- Stub endpoints return **HTTP 200** with legacy-compatible mock bodies
- Real endpoints function normally
- Use only for backward-compatibility testing with legacy clients

### Setting Absent (env var unset)

Uses default value `true` from Pydantic `Settings` class.

### Invalid Values

Non-parseable strings cause Pydantic `ValidationError` at application startup.

---

## Real Endpoints (Always Active)

These endpoints bypass the compatibility flag entirely:

| Route | Behavior |
|-------|----------|
| POST /player/profile/load | DB query → full profile |
| POST /player/login | DB update → login response |
| POST /player/register | DB write → registration |
| POST /version | Config values → version info |
| POST /resource | File read → c_resource.json |
| GET /health | Infrastructure check |
| GET /ready | DB connectivity check |

---

## Stub Endpoints (Gated by legacy_compatibility_mode)

### Legacy-compatible responses (when mode=true)

| Route | Response | Legacy Source |
|-------|----------|---------------|
| POST /matching/server | `{"ip_addr":"<matcher>:<pb_port>"}` | starwing.js:365-368 |
| POST /matching/match_id/generate | `{"match_id":<random_int>}` | starwing.js:435-436 |
| POST /matching/* fallback | `{}` | starwing.js:447 |
| POST /player/login_bonus | `{"result":1,"login_bonuses":[],"update_items":{}}` | starwing.js:547-551 |
| POST /player/* fallback | `{"result":1}` | starwing.js:588-590 |
| POST /ranking/* fallback | `{}` | starwing.js:483 (deafult) |
| POST /game_data/* fallback | `{"result":1}` | starwing.js:734-736 |
| POST /battle/* fallback | `{"result":1}` | starwing.js:773-775 |
| POST /mission/* fallback | `{}` | starwing.js:611-612 |
| POST /credit/* fallback | `{}` | starwing.js:628-629 |
| POST /tutorial/* fallback | `{"result":1}` | starwing.js:646-648 |

### Always 501 (regardless of legacy mode)

These endpoints cannot produce the real legacy response without DB/file implementations:

| Route | Reason | Legacy Source |
|-------|--------|---------------|
| POST /ranking/national | Requires c_rankingNational.json | starwing.js:460 |
| POST /ranking/location | Requires c_rankingStore.json | starwing.js:464 |
| POST /ranking/prefecture | Requires c_rankingPrefecture.json | starwing.js:468 |
| POST /ranking/event | Requires c_rankingEvent.json | starwing.js:472 |
| POST /ranking/weapon | Requires c_rankingWeapon_r*.json | starwing.js:477 |
| POST /game_data/load | Complex DB query (15+ tables) | playerProfile.js:87-296 |
| POST /game_data/load/mission | DB query result | playerProfile.js:74-86 |
| POST /game_data/save | Complex DB writes (15+ UPSERTs) | playerProfile.js:438-722 |
| POST /battle/record_2on2 | Complex ranking/reward object | battleRecorder.js:5-44 |

All 501 responses include:
- Status: 501
- Header: `x-legacy-compat: false`
- Body: `{"error":"not_implemented","endpoint":"...","corrid":"uuid"}`

---

## False Successes Removed

This audit removed all semantically false `{"result":1}` responses where the legacy source returns something different:

| Route | Previous (False) | Correct (Legacy) |
|-------|------------------|-------------------|
| /matching/server | `{"result":1,"servers":[]}` | `{"ip_addr":"paradox.yourdomain.com:6666"}` |
| /matching/match_id/generate | `{"result":1,"match_id":""}` | `{"match_id":42381}` (random int) |
| /matching/* fallback | `{"result":1}` | `{}` |
| /ranking/national | `{"result":1,"ranking":[]}` | 501 (requires file) |
| /ranking/location | `{"result":1,"ranking":[]}` | 501 (requires file) |
| /ranking/prefecture | `{"result":1,"ranking":[]}` | 501 (requires file) |
| /ranking/event | `{"result":1,"ranking":[]}` | 501 (requires file) |
| /ranking/weapon | `{"result":1,"ranking":[]}` | 501 (requires file) |
| /ranking/* fallback | `{"result":1}` | `{}` |
| /game_data/load | `{"result":1,"game_data":{}}` | 501 (requires DB) |
| /game_data/load/mission | `{"result":1,"missions":[]}` | 501 (requires DB) |
| /game_data/save | `{"result":1}` | 501 (requires DB) |
| /battle/record_2on2 | `{"result":1}` | 501 (requires DB) |

---

## Not Implemented (No Python Route)

These routes exist in legacy JS but have no Python equivalent:

- POST /mock/matching/server
- POST /mock/*

---

## Recommendations

1. **Implement file-based responses** for /ranking/* endpoints using the c_ranking*.json files.
2. **Implement DB-backed handlers** for /game_data/load, /game_data/load/mission, /game_data/save.
3. **Implement battle recording** for /battle/record_2on2.
4. **Replicate route-specific `x-galaxy-api` header values** if legacy client validation depends on them.
