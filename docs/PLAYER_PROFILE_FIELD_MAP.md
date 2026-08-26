# PLAYER_PROFILE_FIELD_MAP.md

Field-by-field trace of the legacy `getProfile()` response to its source.

## Source Files

| File | Role |
|------|------|
| `legacy-js/js/starwing/playerProfile.js:297-350` | `getProfile()` method – builds profile response |
| `legacy-js/js/starwing/playerProfile.js:26-73` | `initWithNesys()` – identity resolution |
| `legacy-js/js/starwing.js:488-507` | HTTP endpoint `/player/profile/load` |
| `legacy-js/paradox.sql:100-127` | `player` table DDL with defaults |
| `server/app/db/models/player.py` | SQLAlchemy model |
| `server/app/api/player.py:42-80` | Python endpoint |

## Response Structure

The legacy `getProfile()` (playerProfile.js:297-350) returns `this.Player` – an object containing:

1. All columns from `SELECT * FROM player WHERE player_id=$1` (or `WHERE nesys_id=$1`)
2. Computed fields added by `getProfile()`

## Field Map

### A. Player Table Columns (SQL → Response)

| # | Field Name | Type | Legacy SQL Column | SQL Default | Legacy Source Line | Python Model | Python Default | Implemented |
|---|-----------|------|-------------------|-------------|-------------------|-------------|---------------|-------------|
| 1 | `player_id` | int | `player_id` (PK, seq) | auto-increment | paradox.sql:101, playerProfile.js:21 | `Player.player_id` | autoincrement | YES |
| 2 | `nesys_id` | string(22) | `nesys_id` | NOT NULL | paradox.sql:102 | `Player.nesys_id` | — | YES |
| 3 | `player_name` | string(50) | `player_name` | `'ＮｏＮａｍｅ'` | paradox.sql:103 | `Player.player_name` | `"ＮｏＮａｍｅ"` | YES |
| 4 | `rank_id` | int | `rank_id` | `0` | paradox.sql:104 | `Player.rank_id` | `0` | YES |
| 5 | `rank_id_2on2` | int | `rank_id_2on2` | `0` | paradox.sql:105 | `Player.rank_id_2on2` | `0` | YES |
| 6 | `title_id` | int | `title_id` | `0` | paradox.sql:106 | `Player.title_id` | `0` | YES |
| 7 | `title_id_2on2` | int | `title_id_2on2` | `0` | paradox.sql:107 | `Player.title_id_2on2` | `0` | YES |
| 8 | `buddy_id` | smallint | `buddy_id` | `0` | paradox.sql:108 | `Player.buddy_id` | `0` | YES |
| 9 | `buddy_intimacy` | smallint | `buddy_intimacy` | `0` | paradox.sql:109 | `Player.buddy_intimacy` | `0` | YES |
| 10 | `line_color_id` | int | `line_color_id` | `0` | paradox.sql:110 | `Player.line_color_id` | `0` | YES |
| 11 | `ranking_pref_name` | string(30) | `ranking_pref_name` | `'東京'` | paradox.sql:111 | `Player.ranking_pref_name` | `"東京"` | YES |
| 12 | `last_ranking_pref_name` | string(30) | `last_ranking_pref_name` | `'東京'` | paradox.sql:112 | `Player.last_ranking_pref_name` | `"東京"` | YES |
| 13 | `match_mode_id` | int | `match_mode_id` | `0` | paradox.sql:113 | `Player.match_mode_id` | `0` | YES |
| 14 | `violation_point` | int | `violation_point` | `0` | paradox.sql:114 | `Player.violation_point` | `0` | YES |
| 15 | `emblem_id` | int | `emblem_id` | `0` | paradox.sql:115 | `Player.emblem_id` | `0` | YES |
| 16 | `line_color_id_2on2` | int | `line_color_id_2on2` | `0` | paradox.sql:116 | `Player.line_color_id_2on2` | `0` | YES |
| 17 | `emblem_id_2on2` | int | `emblem_id_2on2` | `0` | paradox.sql:117 | `Player.emblem_id_2on2` | `0` | YES |
| 18 | `birth_day` | int | `birth_day` | `1` | paradox.sql:118 | `Player.birth_day` | `1` | YES |
| 19 | `birth_month` | int | `birth_month` | `1` | paradox.sql:119 | `Player.birth_month` | `1` | YES |
| 20 | `mecha_set_id` | int | `mecha_set_id` | `0` | paradox.sql:120 | `Player.mecha_set_id` | `0` | YES |
| 21 | `side_weapon_id` | int | `side_weapon_id` | `0` | paradox.sql:121 | `Player.side_weapon_id` | `0` | YES |
| 22 | `mecha_preset_id` | int | `mecha_preset_id` | `0` | paradox.sql:122 | `Player.mecha_preset_id` | `0` | YES |
| 23 | `rank_point` | int | `rank_point` | `0` | paradox.sql:123 | `Player.rank_point` | `0` | YES |
| 24 | `max_rank_id` | int | `max_rank_id` | `0` | paradox.sql:124 | `Player.max_rank_id` | `0` | YES |
| 25 | `rank_point_2on2` | int | `rank_point_2on2` | `0` | paradox.sql:125 | `Player.rank_point_2on2` | `0` | YES |
| 26 | `max_rank_id_2on2` | int | `max_rank_id_2on2` | `0` | paradox.sql:126 | `Player.max_rank_id_2on2` | `0` | YES |

### B. Computed Fields Added by `getProfile()`

| # | Field Name | Type | Legacy Source Line | SQL / Computation | Default Value | Python Location | Implemented |
|---|-----------|------|-------------------|-------------------|---------------|----------------|-------------|
| 27 | `same_day_login_count` | int | playerProfile.js:301-303 | `SELECT COUNT(id) AS same_day_login_count FROM player_logins WHERE date_trunc('day', ts_when) = $1 AND player_id=$2` | `0` (from COUNT) | NOT IMPLEMENTED | NO |
| 28 | `total_login_days` | int | playerProfile.js:306-308 | `SELECT COUNT(DISTINCT(date_trunc('day', ts_when))) AS total_login_days FROM player_logins WHERE player_id=$1` | `0` (from COUNT) | NOT IMPLEMENTED | NO |
| 29 | `consecutive_login_days` | int | playerProfile.js:311 | `this.Player.same_day_login_count ? 1 : 0` | `0` | NOT IMPLEMENTED | NO |
| 30 | `last_pref_ranking_order_id` | int | playerProfile.js:340 | hardcoded `0` | `0` | NOT IMPLEMENTED | NO |
| 31 | `pref_ranking_top_player_count` | int | playerProfile.js:341 | hardcoded `0` | `0` | NOT IMPLEMENTED | NO |
| 32 | `official_player_type_id` | int | playerProfile.js:342 | hardcoded `0` | `0` | NOT IMPLEMENTED | NO |

### C. Emblem Object (Hardcoded in `getProfile()`)

| # | Field Name | Type | Legacy Source Line | Value | Implemented |
|---|-----------|------|-------------------|-------|-------------|
| 33 | `emblem` | object | playerProfile.js:314 | `{}` | NO |
| 33a | `emblem.outline` | object | playerProfile.js:315 | `{}` | NO |
| 33b | `emblem.outline.part_id` | int | playerProfile.js:316 | `0` | NO |
| 33c | `emblem.outline.offset` | array[int,int] | playerProfile.js:317 | `[0,0]` | NO |
| 33d | `emblem.outline.scale` | array[int,int] | playerProfile.js:318 | `[1,1]` | NO |
| 33e | `emblem.outline.angle` | int | playerProfile.js:319 | `0` | NO |
| 33f | `emblem.main_design` | object | playerProfile.js:320 | `{}` | NO |
| 33g | `emblem.main_design.part_id` | int | playerProfile.js:321 | `0` | NO |
| 33h | `emblem.main_design.offset` | array[int,int] | playerProfile.js:322 | `[0,0]` | NO |
| 33i | `emblem.main_design.scale` | array[int,int] | playerProfile.js:323 | `[1,1]` | NO |
| 33j | `emblem.main_design.angle` | int | playerProfile.js:324 | `0` | NO |
| 33k | `emblem.sub_design` | object | playerProfile.js:325 | `{}` | NO |
| 33l | `emblem.sub_design.part_id` | int | playerProfile.js:326 | `0` | NO |
| 33m | `emblem.sub_design.offset` | array[int,int] | playerProfile.js:327 | `[0,0]` | NO |
| 33n | `emblem.sub_design.scale` | array[int,int] | playerProfile.js:328 | `[1,1]` | NO |
| 33o | `emblem.sub_design.angle` | int | playerProfile.js:329 | `0` | NO |

### D. Progresses Array

| # | Field Name | Type | Legacy Source Line | SQL | Implemented |
|---|-----------|------|-------------------|-----|-------------|
| 34 | `progresses` | array | playerProfile.js:331-338 | `SELECT progress_key,status FROM player_progress WHERE player_id=$1` | NO (empty array returned) |

Each element:
| Sub-field | Type | Source |
|-----------|------|--------|
| `progress_key` | string(35) | player_progress.progress_key |
| `status` | smallint | player_progress.status |

## Response Headers

| Header | Legacy Value | Python Value | Source |
|--------|-------------|-------------|--------|
| `Content-type` | `application/json` | `application/json` (FastAPI default) | starwing.js:496 |
| `x-galaxy-api` | `player/profile` | `*/*` | starwing.js:498 vs player.py:49 |
| `x-galaxy-api-id` | echoed from request | echoed from request | starwing.js:497 vs player.py:50-51 |

## Identity Resolution Flow

```
POST /player/profile/load
  body: { "nesys_id": "..." }
  
Legacy (starwing.js:488-507):
  1. pp = new pp.PlayerProfile()
  2. pt.initWithNesys(pgdb, req.body.nesys_id)
     → SELECT * FROM player WHERE nesys_id=$1
     → If not found: INSERT INTO player(nesys_id) VALUES ($1) RETURNING player_id
     → Then SELECT * FROM player WHERE player_id=$1
  3. res.send(JSON.stringify(await pt.getProfile()))
     → getProfile() adds computed fields, returns player object

Python (player.py:42-80):
  1. Extract nesys_id from body
  2. Query "SELECT id, name, level, exp, gold, jewels FROM players WHERE nesys_id = :nid"
  3. Return _ok(player_id=..., name=..., ...) or _ok(result=0)

KNOWN DEVIATIONS:
  - Python queries "players" table (wrong) instead of "player" table
  - Python queries non-existent columns (level, exp, gold, jewels)
  - Python does not auto-create player on NESYS ID miss
  - Python does not compute same_day_login_count, total_login_days, consecutive_login_days
  - Python does not return emblem structure
  - Python does not return progresses array from player_progress table
  - Python returns result-wrapped response; legacy returns raw player object
  - x-galaxy-api header is '*/*' instead of 'player/profile'
```

## Summary Statistics

| Category | Total Fields | Implemented | Missing |
|----------|-------------|-------------|---------|
| Player table columns | 26 | 26 | 0 |
| Computed fields | 6 | 0 | 6 |
| Emblem object | 15 | 0 | 15 |
| Progresses array | 1 (+sub) | 0 | 1 |
| **Total** | **48** | **26** | **22** |
