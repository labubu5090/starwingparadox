# Database Model Parity Audit

> **Source**: `legacy-js/paradox.sql`, `server/app/db/models/`, `server/app/db/repositories/`, `server/app/services/`, `legacy-js/js/starwing/*.js`
> **Date**: 2026-08-26
> **Status**: Full audit

---

## Status Legend

| Status | Meaning |
|--------|---------|
| `EXACT_LEGACY_MAPPING` | Model fields exactly match legacy schema columns, types, and defaults |
| `SAFE_PARTIAL_MAPPING` | Model covers all legacy columns used by endpoints; extras are safe additions |
| `MAPPING_MISMATCH` | Field names, types, defaults, or constraints differ between model and legacy |
| `MODEL_NOT_CREATED` | Legacy table has no corresponding Python model |
| `SOURCE_AMBIGUOUS` | Cannot determine exact legacy behavior from available JS source |
| `POSTGRESQL_VALIDATION_REQUIRED` | Requires live PostgreSQL testing to confirm behavior |

---

## Table: `player`

**Status**: `SAFE_PARTIAL_MAPPING`

### Legacy Schema (paradox.sql:100-127)

| Column | SQL Type | Default | Nullable |
|--------|----------|---------|----------|
| player_id | integer (PK, serial) | nextval | NO |
| nesys_id | varchar(22) NOT NULL | - | NO |
| player_name | varchar(50) | 'ＮｏＮａｍｅ' | YES |
| rank_id | integer | 0 | YES |
| rank_id_2on2 | integer | 0 | YES |
| title_id | integer | 0 | YES |
| title_id_2on2 | integer | 0 | YES |
| buddy_id | smallint | 0 | YES |
| buddy_intimacy | smallint | 0 | YES |
| line_color_id | integer | 0 | YES |
| ranking_pref_name | varchar(30) | '東京' | YES |
| last_ranking_pref_name | varchar(30) | '東京' | YES |
| match_mode_id | integer | 0 | YES |
| violation_point | integer | 0 | YES |
| emblem_id | integer | 0 | YES |
| line_color_id_2on2 | integer | 0 | YES |
| emblem_id_2on2 | integer | 0 | YES |
| birth_day | integer | 1 | YES |
| birth_month | integer | 1 | YES |
| mecha_set_id | integer | 0 | YES |
| side_weapon_id | integer | 0 | YES |
| mecha_preset_id | integer | 0 | YES |
| rank_point | integer | 0 | YES |
| max_rank_id | integer | 0 | YES |
| rank_point_2on2 | integer | 0 | YES |
| max_rank_id_2on2 | integer | 0 | YES |

### Python Model (server/app/db/models/player.py)

All 26 legacy columns are present with correct types and defaults.

### Legacy JS SQL (playerProfile.js)

- **Read**: `SELECT * FROM player WHERE player_id=$1` (line 15), `SELECT * FROM player WHERE nesys_id=$1` (line 35)
- **Write**: Dynamic UPDATE via `playerRegister` (line 403): builds `UPDATE player SET k=$p` from request body keys
- **Individual field updates**: `title_id_2on2`, `mecha_set_id`, `emblem_id_2on2`, `line_color_id_2on2`, `side_weapon_id`, `mecha_preset_id`, `rank_point`, `max_rank_id`, `rank_point_2on2`, `max_rank_id_2on2`, `buddy_id` (lines 662-704)
- **Insert**: `INSERT INTO player(nesys_id) VALUES ($1) RETURNING player_id` (line 41)

### Mismatches

1. **Unique constraint on nesys_id**: Legacy has NO unique index on `nesys_id`. Python model also lacks it. This is a data integrity risk but matches legacy behavior.
2. **player_name**: Legacy SQL column is `varchar(50)` with default `'ＮｏＮａｍｅ'`. Python model uses `String(50)` with `default="ＮｏＮａｍｅ"` -- matches.
3. **Dynamic UPDATE in playerRegister**: Legacy JS builds UPDATE from arbitrary request body keys. Python `PlayerRepository.update_player` uses `**kwargs` -- matches.
4. **nesys_id NOT NULL**: Legacy SQL declares `NOT NULL`. Python model uses `Mapped[str]` without `nullable=False` -- SQLAlchemy default for non-optional `Mapped[str]` is `NOT NULL`, so this matches.

---

## Table: `player_buddies`

**Status**: `EXACT_LEGACY_MAPPING`

### Legacy Schema (paradox.sql:136-143)

| Column | SQL Type | Default | Nullable |
|--------|----------|---------|----------|
| id | integer (PK, serial) | nextval | NO |
| player_id | integer NOT NULL | - | NO |
| buddy_id | integer NOT NULL | - | NO |
| buddy_key | varchar(35) NOT NULL | - | NO |
| buddy_value | varchar(35) | 0 | YES |

**Unique index**: (player_id, buddy_id, buddy_key)

### Python Model (server/app/db/models/player_buddies.py)

All columns match. UniqueConstraint on (player_id, buddy_id, buddy_key) matches legacy unique index.

### Legacy JS SQL

- **Read**: `SELECT buddy_id, buddy_key, buddy_value FROM player_buddies WHERE player_id=$1` (line 111)
- **Write**: `INSERT ... ON CONFLICT (player_id,buddy_id,buddy_key) DO UPDATE SET buddy_value = excluded.buddy_value` (line 462-465)

### Notes

- `buddy_value` defaults to `'0'` (string) in both legacy and Python.
- Legacy JS reads only `buddy_id, buddy_key, buddy_value` (not `id`, `player_id`). Python model includes all columns -- safe.
- Repository `upsert_buddy` matches legacy UPSERT pattern exactly.

---

## Table: `player_buddy_win_poses`

**Status**: `EXACT_LEGACY_MAPPING`

### Legacy Schema (paradox.sql:27-33)

| Column | SQL Type | Default | Nullable |
|--------|----------|---------|----------|
| id | integer (PK, serial) | nextval | NO |
| player_id | integer NOT NULL | - | NO |
| buddy_id | integer NOT NULL | - | NO |
| win_pose_id | integer NOT NULL | - | NO |
| status | integer | 0 | YES |

**Unique index**: (player_id, buddy_id, win_pose_id)

### Python Model

All columns match. UniqueConstraint matches.

### Legacy JS SQL

- **Read**: `SELECT * FROM player_buddy_win_poses WHERE player_id=$1` (line 154). Strips `id` and `player_id` from response.
- **Write**: `INSERT ... ON CONFLICT (player_id, buddy_id, win_pose_id) DO UPDATE SET status = excluded.status` (line 602-605)

---

## Table: `player_emblem_parts`

**Status**: `EXACT_LEGACY_MAPPING`

### Legacy Schema (paradox.sql:173-178)

| Column | SQL Type | Default | Nullable |
|--------|----------|---------|----------|
| id | integer (PK, serial) | nextval | NO |
| player_id | integer NOT NULL | - | NO |
| part_id | integer NOT NULL | - | NO |
| status | integer | 0 | YES |

**Unique index**: (player_id, part_id)

### Python Model

Matches. UniqueConstraint on (player_id, part_id).

### Legacy JS SQL

- **Read**: `SELECT * FROM player_emblem_parts WHERE player_id=$1` (line 191). Strips `id` and `player_id`.
- **Write**: `INSERT ... ON CONFLICT (player_id,part_id) DO UPDATE SET status = excluded.status` (line 562-565)

---

## Table: `player_emblems`

**Status**: `MAPPING_MISMATCH`

### Legacy Schema (paradox.sql:209-233)

| Column | SQL Type | Default | Nullable |
|--------|----------|---------|----------|
| id | integer (PK, serial) | nextval | NO |
| player_id | integer NOT NULL | - | NO |
| emblem_id | integer NOT NULL | - | NO |
| outline_part_id | integer NOT NULL | - | NO |
| outline_offset_x | integer NOT NULL | - | NO |
| outline_offset_y | integer NOT NULL | - | NO |
| outline_scale_x | integer NOT NULL | - | NO |
| outline_scale_y | integer NOT NULL | - | NO |
| outline_angle | integer NOT NULL | - | NO |
| main_design_part_id | integer NOT NULL | - | NO |
| main_design_offset_x | integer NOT NULL | - | NO |
| main_design_offset_y | integer NOT NULL | - | NO |
| main_design_scale_x | integer NOT NULL | - | NO |
| main_design_scale_y | integer NOT NULL | - | NO |
| main_design_angle | integer NOT NULL | - | NO |
| sub_design_part_id | integer NOT NULL | - | NO |
| sub_design_offset_x | integer NOT NULL | - | NO |
| sub_design_offset_y | integer NOT NULL | - | NO |
| sub_design_scale_x | integer NOT NULL | - | NO |
| sub_design_scale_y | integer NOT NULL | - | NO |
| sub_design_angle | integer NOT NULL | - | NO |
| status | integer | 0 | YES |
| editable | boolean | false | YES |

**Unique index**: (player_id, emblem_id)

### Python Model (server/app/db/models/player_emblems.py)

**CRITICAL MISMATCH**: The Python model has completely different field names and structure:

| Python Field | Legacy Column | Mismatch |
|--------------|---------------|----------|
| `outline_type` | `outline_part_id` | Name mismatch |
| `outline_color_r` | (does not exist) | Extra field |
| `outline_color_g` | (does not exist) | Extra field |
| `outline_color_b` | (does not exist) | Extra field |
| `outline_color_a` | (does not exist) | Extra field |
| `outline_size` | `outline_scale_x` / `outline_scale_y` | Name + split mismatch |
| `outline_rot` | `outline_angle` | Name mismatch |
| `outline_pos_x` | `outline_offset_x` | Name mismatch |
| `outline_pos_y` | `outline_offset_y` | Name mismatch |
| `main_design_type` | `main_design_part_id` | Name mismatch |
| `main_design_color_r` | (does not exist) | Extra field |
| `main_design_color_g` | (does not exist) | Extra field |
| `main_design_color_b` | (does not exist) | Extra field |
| `main_design_color_a` | (does not exist) | Extra field |
| `main_design_size` | `main_design_scale_x` / `main_design_scale_y` | Name + split mismatch |
| `main_design_rot` | `main_design_angle` | Name mismatch |
| `main_design_pos_x` | `main_design_offset_x` | Name mismatch |
| `main_design_pos_y` | `main_design_offset_y` | Name mismatch |
| `sub_design_type` | `sub_design_part_id` | Name mismatch |
| `sub_design_color_*` | (does not exist) | Extra fields |
| `sub_design_size` | `sub_design_scale_x` / `sub_design_scale_y` | Name + split mismatch |
| `sub_design_rot` | `sub_design_angle` | Name mismatch |
| `sub_design_pos_x` | `sub_design_offset_x` | Name mismatch |
| `sub_design_pos_y` | `sub_design_offset_y` | Name mismatch |

### Legacy JS SQL

- **Read**: `SELECT * FROM player_emblems WHERE player_id=$1` (line 163). Transforms columns into nested objects:
  ```js
  emblem.outline.part_id = res.rows[k].outline_part_id;
  emblem.outline.offset = [res.rows[k].outline_offset_x, res.rows[k].outline_offset_y];
  emblem.outline.scale = [res.rows[k].outline_scale_x, res.rows[k].outline_scale_y];
  emblem.outline.angle = res.rows[k].outline_angle;
  ```
- **Write**: Full UPSERT with all 22 fields (lines 516-557)

### Impact

The Python model CANNOT correctly read or write the legacy `player_emblems` table. The column names are fundamentally different. The Python model appears to use a redesigned schema with RGBA color fields instead of the legacy part_id + offset/scale/angle structure. This is the most critical mismatch in the codebase.

---

## Table: `player_line_colors`

**Status**: `EXACT_LEGACY_MAPPING`

### Legacy Schema (paradox.sql:264-269)

| Column | SQL Type | Default |
|--------|----------|---------|
| id | integer (PK) | nextval |
| player_id | integer NOT NULL | - |
| line_color_id | integer NOT NULL | - |
| status | integer | 0 |

**Unique index**: (player_id, line_color_id)

### Python Model

Matches. UniqueConstraint matches.

### Legacy JS SQL

- **Write**: `INSERT ... ON CONFLICT (player_id, line_color_id) DO UPDATE SET status = excluded.status` (line 613-618)

---

## Table: `player_logins`

**Status**: `MAPPING_MISMATCH`

### Legacy Schema (paradox.sql:300-308)

| Column | SQL Type | Default | Nullable |
|--------|----------|---------|----------|
| id | integer (PK) | nextval | NO |
| player_id | integer NOT NULL | - | NO |
| ip_addr | inet NOT NULL | - | NO |
| location_id | integer | 0 | YES |
| client_version | integer | 0 | YES |
| data_version | integer | 0 | YES |
| ts_when | timestamp without time zone NOT NULL | - | NO |

### Python Model (server/app/db/models/player_logins.py)

| Issue | Detail |
|-------|--------|
| `ip_addr` type | Legacy: `inet`. Python: `String`. Mismatch. |
| `ts_when` nullability | Legacy: `NOT NULL`. Python: `nullable=True`. Mismatch. |
| `ts_when` type hint | Python: `Mapped[str | None]`. Should be `Mapped[datetime]`. |

### Legacy JS SQL

- **Write**: `INSERT INTO player_logins (player_id,ip_addr,ts_when,location_id,client_version,data_version) VALUES ($1,$2,now(),$3,$4,$5)` (line 353)
- **Read**: `SELECT COUNT(id) AS same_day_login_count FROM player_logins WHERE date_trunc('day', ts_when) = $1 AND player_id=$2` (line 94, 301, 368)
- **Read**: `SELECT COUNT(DISTINCT(date_trunc('day', ts_when))) AS total_login_days FROM player_logins WHERE player_id=$1` (line 99, 306, 373)

### Impact

1. `inet` type vs `String`: PostgreSQL `inet` type stores IP addresses with optional subnet. `String` works for storage but loses inet-specific functions. For the legacy use case (just storing IPs), `String` is functionally equivalent.
2. `ts_when` nullable mismatch: Legacy is `NOT NULL`, Python allows `NULL`. Could insert null timestamps that legacy would reject.

---

## Table: `player_mecha_colors`

**Status**: `EXACT_LEGACY_MAPPING`

### Legacy Schema (paradox.sql:64-69)

| Column | SQL Type | Default |
|--------|----------|---------|
| id | integer (PK) | nextval |
| player_id | integer NOT NULL | - |
| mecha_color_id | integer NOT NULL | - |
| status | integer | 0 |

**Unique index**: (player_id, mecha_color_id)

### Python Model

Matches. UniqueConstraint matches.

---

## Table: `player_mecha_set_parts`

**Status**: `EXACT_LEGACY_MAPPING`

### Legacy Schema (paradox.sql:339-347)

| Column | SQL Type | Default |
|--------|----------|---------|
| id | integer (PK) | nextval |
| player_id | integer NOT NULL | - |
| mecha_set_id | integer NOT NULL | - |
| part_id | integer NOT NULL | - |
| mecha_id | integer NOT NULL | - |
| design_id | integer | 0 |
| color_id | integer | 0 |

**Unique index**: (player_id, mecha_set_id, part_id)

### Python Model

Matches. UniqueConstraint matches.

### Legacy JS SQL

- **Write**: `INSERT ... ON CONFLICT (player_id,mecha_set_id,part_id) DO UPDATE SET mecha_id, design_id, color_id` (line 588-592)

---

## Table: `player_mecha_sets`

**Status**: `EXACT_LEGACY_MAPPING`

### Legacy Schema (paradox.sql:378-392)

| Column | SQL Type | Default | Nullable |
|--------|----------|---------|----------|
| id | integer (PK) | nextval | NO |
| player_id | integer NOT NULL | - | NO |
| mecha_set_id | integer NOT NULL | - | NO |
| mecha_setbonus_id | integer NOT NULL | - | NO |
| weapon_set_id | integer NOT NULL | - | NO |
| is_decal | boolean | false | YES |
| favorite | boolean | false | YES |
| use_count | integer | 0 | YES |
| use_time | integer | 0 | YES |
| status | integer | 0 | YES |
| win_count | integer | NULL | YES |
| winning_streaks | integer | NULL | YES |

**Unique index**: (player_id, mecha_set_id)

### Python Model

Matches. `win_count` and `winning_streaks` correctly nullable.

### Legacy JS SQL

- **Write**: Full UPSERT with all 11 columns (line 573-578)

---

## Table: `player_missions`

**Status**: `EXACT_LEGACY_MAPPING`

### Legacy Schema (paradox.sql:422-430)

| Column | SQL Type | Default |
|--------|----------|---------|
| id | integer (PK) | nextval |
| player_id | integer NOT NULL | - |
| mission_id | integer NOT NULL | - |
| clear_count | integer | 0 |
| clear_num | integer | 0 |
| status | integer | 0 |
| mission_status | integer | 0 |

**Unique index**: (player_id, mission_id)

### Python Model

Matches.

### Legacy JS SQL

- **Read**: `SELECT mission_id,clear_count,clear_num,status,mission_status FROM player_missions WHERE player_id=$1` (lines 77, 144, 353, 36, 713)
- **Write**: `INSERT ... ON CONFLICT (player_id,mission_id) DO UPDATE SET clear_count, clear_num, status, mission_status` (line 496-499)

### Note

Legacy JS `playerSaveGameData` re-reads ALL missions after every save iteration (line 713). This is a performance concern but not a model mismatch.

---

## Table: `player_options`

**Status**: `EXACT_LEGACY_MAPPING`

### Legacy Schema (paradox.sql:461-466)

| Column | SQL Type | Default |
|--------|----------|---------|
| id | integer (PK) | nextval |
| player_id | integer NOT NULL | - |
| option_key | varchar(35) NOT NULL | - |
| value_num | integer | 0 |

**Unique index**: (player_id, option_key)

### Python Model

Matches.

### Legacy JS SQL

- **Write**: `INSERT ... ON CONFLICT (player_id,option_key) DO UPDATE SET value_num = excluded.value_num` (line 445-448)

---

## Table: `player_progress`

**Status**: `EXACT_LEGACY_MAPPING`

### Legacy Schema (paradox.sql:519-524)

| Column | SQL Type | Default |
|--------|----------|---------|
| id | integer (PK) | nextval |
| player_id | integer NOT NULL | - |
| progress_key | varchar(35) NOT NULL | - |
| status | smallint | 0 |

**Unique index**: (player_id, progress_key)

### Python Model

Matches. Uses `SmallInteger` for `status` -- matches legacy `smallint`.

### Legacy JS SQL

- **Write**: `INSERT ... ON CONFLICT (player_id,progress_key) DO UPDATE SET status = excluded.status` (line 425-428, 486-489)

---

## Table: `player_side_weapons`

**Status**: `EXACT_LEGACY_MAPPING`

### Legacy Schema (paradox.sql:555-562)

| Column | SQL Type | Default |
|--------|----------|---------|
| id | integer (PK) | nextval |
| player_id | integer NOT NULL | - |
| side_weapon_id | integer NOT NULL | - |
| use_count | integer | 0 |
| use_time | integer | 0 |
| status | integer | 0 |

**Unique index**: (player_id, side_weapon_id)

### Python Model

Matches.

---

## Table: `player_titles`

**Status**: `EXACT_LEGACY_MAPPING`

### Legacy Schema (paradox.sql:593-598)

| Column | SQL Type | Default |
|--------|----------|---------|
| id | integer (PK) | nextval |
| player_id | integer NOT NULL | - |
| title_id | integer NOT NULL | - |
| status | integer | 0 |

**Unique index**: (player_id, title_id)

### Python Model

Matches.

---

## Table: `player_weapon_set`

**Status**: `EXACT_LEGACY_MAPPING`

### Legacy Schema (paradox.sql:629-636)

| Column | SQL Type | Default |
|--------|----------|---------|
| id | integer (PK) | nextval |
| player_id | integer NOT NULL | - |
| weapon_set_id | integer NOT NULL | - |
| use_count | integer | 0 |
| use_time | integer | 0 |
| status | integer | 0 |

**Unique index**: (player_id, weapon_set_id)

### Python Model

Matches.

---

## Table: `player_weapon_set_slots`

**Status**: `EXACT_LEGACY_MAPPING`

### Legacy Schema (paradox.sql:645-653)

| Column | SQL Type | Default |
|--------|----------|---------|
| id | integer (PK) | nextval |
| player_id | integer NOT NULL | - |
| weapon_set_id | integer NOT NULL | - |
| slot_id | integer NOT NULL | - |
| weapon_id | integer NOT NULL | - |
| use_count | integer | 0 |
| use_time | integer | 0 |

**Unique index**: (player_id, weapon_set_id, slot_id)

### Python Model

Matches.

---

## Endpoint-to-Table Mapping

### `POST /player/profile/load` (playerProfile.js `getProfile`)

| Operation | Table | Columns Read |
|-----------|-------|-------------|
| SELECT | player | * (all columns) |
| SELECT | player_logins | COUNT(DISTINCT date_trunc('day', ts_when)) |
| SELECT | player_progress | progress_key, status |

**Python Service**: `PlayerService.load_profile_by_nesys` -- reads only `player_id, nesys_id, player_name, rank_id`. Missing `progresses`, `total_login_days`, `same_day_login_count`. **Partial mapping**.

### `POST /player/login` (playerProfile.js `playerLogin`)

| Operation | Table | Columns Written/Read |
|-----------|-------|---------------------|
| INSERT | player_logins | player_id, ip_addr, ts_when(now), location_id, client_version, data_version |
| SELECT | player_progress | progress_key, status |
| SELECT | player_logins | COUNT for login stats |

**Python Service**: `PlayerService.login_player` -- reads player only. Does NOT insert login record or compute stats. **Partial mapping**.

### `POST /player/register` (playerProfile.js `playerRegister`)

| Operation | Table | Columns Written |
|-----------|-------|-----------------|
| UPDATE | player | Dynamic from request body |
| INSERT/UPSERT | player_progress | player_id, progress_key, status |

**Python Service**: `PlayerService.register_player` -- only calls `create_player(nesys_id)`. Does NOT process dynamic fields or progresses. **Partial mapping**.

### `POST /game_data/load` (playerProfile.js `playerLoadGameData`)

| Operation | Table | Columns Read |
|-----------|-------|-------------|
| SELECT | player_logins | Login count stats |
| SELECT | player_buddies | buddy_id, buddy_key, buddy_value |
| SELECT | player_progress | progress_key, status |
| SELECT | player_options | option_key, value_num |
| SELECT | player_missions | mission_id, clear_count, clear_num, status, mission_status |
| SELECT | player_buddy_win_poses | * (minus id, player_id) |
| SELECT | player_emblems | * (minus id, player_id) |
| SELECT | player_emblem_parts | * (minus id, player_id) |
| SELECT | player_titles | * (minus id, player_id) |
| SELECT | player_line_colors | * (minus id, player_id) |
| SELECT | player_mecha_sets | * (minus id, player_id) |
| SELECT | player_mecha_set_parts | * (minus id, player_id) |
| SELECT | player_mecha_colors | * (minus id, player_id) |
| SELECT | player_weapon_set | * (minus id, player_id) |
| SELECT | player_weapon_set_slots | * (minus id, player_id) |
| SELECT | player_side_weapons | * (minus id, player_id) |

**Python Service**: `PlayerService.load_game_data` -- reads only `player_id`. Does NOT query any sub-tables. **Major gap**.

### `POST /game_data/load/mission` (playerProfile.js `playerLoadGameDataMissions`)

| Operation | Table | Columns Read |
|-----------|-------|-------------|
| SELECT | player_missions | mission_id, clear_count, clear_num, status, mission_status |

**Python Service**: `PlayerService.load_game_data_missions` -- reads only `player_id`. Does NOT query missions. **Gap**.

### `POST /game_data/save` (playerProfile.js `playerSaveGameData`)

| Operation | Table | Columns Written |
|-----------|-------|-----------------|
| UPSERT | player_options | player_id, option_key, value_num |
| UPSERT | player_buddies | player_id, buddy_id, buddy_key, buddy_value |
| UPSERT | player_progress | player_id, progress_key, status |
| UPSERT | player_missions | player_id, mission_id, clear_count, clear_num, status, mission_status |
| UPSERT | player_titles | player_id, title_id, status |
| UPSERT | player_emblems | All 22 columns |
| UPSERT | player_emblem_parts | player_id, part_id, status |
| UPSERT | player_mecha_sets | All 11 columns |
| UPSERT | player_mecha_set_parts | player_id, mecha_set_id, part_id, mecha_id, design_id, color_id |
| UPSERT | player_buddy_win_poses | player_id, buddy_id, win_pose_id, status |
| UPSERT | player_line_colors | player_id, line_color_id, status |
| UPSERT | player_mecha_colors | player_id, mecha_color_id, status |
| UPSERT | player_weapon_set | player_id, weapon_set_id, use_count, use_time, status |
| UPSERT | player_weapon_set_slots | player_id, weapon_set_id, slot_id, weapon_id, use_count, use_time |
| UPSERT | player_side_weapons | player_id, side_weapon_id, use_count, use_time, status |
| UPDATE | player | title_id_2on2, mecha_set_id, emblem_id_2on2, line_color_id_2on2, side_weapon_id, mecha_preset_id, rank_point, max_rank_id, rank_point_2on2, max_rank_id_2on2, buddy_id |

**Python Service**: `PlayerService.save_game_data` -- returns `{"result": 0, "message": "Saved"}` without processing any data. **Complete gap**.

### `POST /battle/record_2on2` (battleRecorder.js)

| Operation | Table | Columns Read |
|-----------|-------|-------------|
| SELECT | player_missions | mission_id, clear_count, clear_num, status, mission_status |

**Python Service**: `BattleService` -- stub. Does NOT read missions. **Gap**.

---

## Repository Layer Analysis

### `GameDataRepository`

The repository layer (`server/app/db/repositories/game_data_repository.py`) implements upsert methods for all sub-tables. However, the `PlayerService` layer does NOT use most of them:

| Repository Method | Used by Service? |
|-------------------|-----------------|
| `upsert_buddy` | No |
| `upsert_buddy_win_pose` | No |
| `upsert_progress` | No |
| `upsert_option` | No |
| `upsert_mission` | No |
| `upsert_title` | No |
| `upsert_emblem_part` | No |
| `upsert_line_color` | No |
| `upsert_mecha_color` | No |
| `upsert_mecha_set_part` | No |
| `upsert_side_weapon` | No |
| `upsert_weapon_set` | No |
| `upsert_weapon_set_slot` | No |

The repository methods exist but are orphaned -- never called from services.

---

## Missing Model Fields Summary

| Table | Field | Issue |
|-------|-------|-------|
| `player_emblems` | (entire structure) | Python model uses completely different field names (see mismatch above) |
| `player_logins` | `ip_addr` | Legacy: `inet`. Python: `String` |
| `player_logins` | `ts_when` | Legacy: `NOT NULL`. Python: `nullable=True` |

---

## Legacy SQL Quirks

1. **No foreign keys**: Legacy schema has zero FK constraints. All `player_id` columns are logically FK but not enforced.
2. **No unique on nesys_id**: Legacy allows duplicate `nesys_id` values (potential data corruption).
3. **All columns nullable except PKs and explicitly NOT NULL**: Most `integer` columns default to 0 and are nullable.
4. **UPSERT pattern**: Legacy uses `INSERT ... ON CONFLICT DO UPDATE` exclusively. No separate INSERT/UPDATE paths.
5. **Buddy data as key-value store**: `player_buddies` stores heterogeneous data (intimacy, skill IDs, win poses, usage stats) as string key-value pairs.
6. **emblem columns use `NOT NULL` without defaults**: `outline_part_id`, `outline_offset_x`, etc. are `NOT NULL` but have no `DEFAULT` -- legacy relies on application always providing values.
7. **`player_missions` re-read after every save**: Legacy JS re-fetches all missions after each save iteration in `playerSaveGameData` (line 713).
8. **Dynamic UPDATE construction**: `playerRegister` builds UPDATE queries from arbitrary request body keys (line 403-414).

---

## Recommendations

1. **Critical**: Fix `player_emblems` model to match legacy column names or document the schema redesign.
2. **Critical**: Wire `PlayerService` to use `GameDataRepository` methods for load/save operations.
3. **High**: Add `ip_addr` column type as `String` (acceptable) or create custom `InetType`.
4. **High**: Remove `nullable=True` from `PlayerLogin.ts_when` to match legacy `NOT NULL`.
5. **Medium**: Add unique constraint on `player.nesys_id` if data integrity is desired.
6. **Medium**: Implement transaction wrapping for `game_data/save` to match legacy atomicity.
7. **Low**: Add FK constraints if referential integrity enforcement is desired.
