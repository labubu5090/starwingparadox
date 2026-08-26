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
- Real endpoints function normally
- Recommended for development and new integrations

### `LEGACY_COMPATIBILITY_MODE=true` (Legacy Mode, DEFAULT)

- Stub endpoints return **HTTP 200** with mock success bodies
- Real endpoints function normally
- Use only for backward-compatibility testing with legacy clients
- **WARNING**: Many mock responses differ from actual legacy server behavior (see Reality Check)

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

## Stub Endpoints (Gated)

### Returns `{"result":1,"login_bonuses":[],"update_items":{}}`
- POST /player/login_bonus

### Returns `{"result":1}`
- POST /player/{fallback}
- POST /matching/{fallback}
- POST /ranking/{fallback}
- POST /game_data/{fallback}
- POST /battle/{fallback}
- POST /tutorial/{fallback}

### Returns `{"result":1,...}` (custom shapes)
- POST /matching/server → `{"result":1,"servers":[]}`
- POST /matching/match_id/generate → `{"result":1,"match_id":""}`
- POST /ranking/national → `{"result":1,"ranking":[]}`
- POST /ranking/location → `{"result":1,"ranking":[]}`
- POST /ranking/prefecture → `{"result":1,"ranking":[]}`
- POST /ranking/event → `{"result":1,"ranking":[]}`
- POST /ranking/weapon → `{"result":1,"ranking":[]}`
- POST /game_data/load → `{"result":1,"game_data":{}}`
- POST /game_data/load/mission → `{"result":1,"missions":[]}`
- POST /game_data/save → `{"result":1}`
- POST /battle/record_2on2 → `{"result":1}`

### Returns `{}`
- POST /mission/{fallback}
- POST /credit/{fallback}

---

## Legacy Parity Gaps

**These stub responses DO NOT match the actual legacy JavaScript server.** See `LEGACY_COMPATIBILITY_REALITY_CHECK.md` for full evidence.

Key discrepancies:

| Route | Legacy Returns | Python Returns (mode=true) |
|-------|---------------|---------------------------|
| /matching/server | `{"ip_addr":"paradox.yourdomain.com:6666"}` | `{"result":1,"servers":[]}` |
| /matching/match_id/generate | `{"match_id":42381}` (random int) | `{"result":1,"match_id":""}` |
| /matching/* | `{}` | `{"result":1}` |
| /ranking/* | File contents (e.g., `c_rankingNational.json`) | `{"result":1,"ranking":[]}` |
| /ranking/* | `{}` (default) | `{"result":1}` |
| /game_data/load | 15+ table query result | `{"result":1,"game_data":{}}` |
| /game_data/load/mission | player_missions query result | `{"result":1,"missions":[]}` |
| /game_data/save | `{result:1, missions:[...]}` (after 15+ UPSERTs) | `{"result":1}` |
| /battle/record_2on2 | Complex object with ranking/rewards | `{"result":1}` |
| /mission/* | `{}` | `{}` ✓ |
| /credit/* | `{}` | `{}` ✓ |

---

## Header Differences

All Python endpoints set `x-galaxy-api: */\*` via `_galaxy_headers()`. Legacy JS uses route-specific values for these endpoints:

| Route | Legacy `x-galaxy-api` value |
|-------|-----------------------------|
| /ranking/national | `ranking/national` |
| /ranking/location | `ranking/location` |
| /ranking/prefecture | `ranking/prefecture` |
| /ranking/event | `ranking/event` |
| /ranking/weapon | `ranking/event` (bug in legacy) |
| /player/profile/load | `player/profile` |
| /player/login | `player/login` |
| /player/login_bonus | `player/login` |
| /player/register | `player/register` |
| /game_data/load/mission | `game_data/load` |
| /game_data/load | `game_data/load` |
| /game_data/save | `game_data/save` |

---

## Not Implemented (No Python Route)

These routes exist in legacy JS but have no Python equivalent:

- POST /mock/matching/server
- POST /mock/*

---

## Recommendations

1. **Do not rely on `LEGACY_COMPATIBILITY_MODE=true` for production legacy client compatibility.** The mock responses have wrong shapes for 9 of 20 stub endpoints.
2. **Implement actual file-based responses** for /ranking/* and /resource endpoints.
3. **Implement DB-backed stubs** for /game_data/load, /game_data/load/mission, /game_data/save, /battle/record_2on2.
4. **Fix response shapes** for /matching/server (`ip_addr` field) and /matching/match_id/generate (random int).
5. **Replicate route-specific `x-galaxy-api` header values** if legacy client validation depends on them.
