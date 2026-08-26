# Game Data Parity Gaps

> Source: `legacy-js/js/starwing.js` lines 653-738
> Python: `server/app/api/game_data.py`
> Repository: `server/app/db/repositories/game_data_repository.py`

---

## Route Inventory

| Route | Legacy Lines | Python Status | Source Provenance |
|-------|-------------|---------------|-------------------|
| `POST /game_data/load/mission` | 653-676 | 501 not_implemented | SOURCE_PROVEN_DATABASE |
| `POST /game_data/load` | 677-698 | 501 not_implemented | SOURCE_PROVEN_DATABASE |
| `POST /game_data/save` | 700-720 | 501 not_implemented | SOURCE_PROVEN_DATABASE |
| `POST /game_data/*` (fallback) | 722-738 | 200 `{result: 1}` (legacy mode) | SOURCE_PROVEN_STATIC |

---

## Source Provenance Categories

### SOURCE_PROVEN_STATIC

Legacy behavior is fully understood from source code. Response is deterministic.

#### `POST /game_data/*` (fallback) - lines 722-738

- **Legacy behavior**: Returns `{result: 1}` with `x-galaxy-api: '*/*'`
- **Python behavior**: Returns `{result: 1}` in legacy mode, 501 in strict mode
- **Database access**: None
- **Parity status**: MATCHED

### SOURCE_PROVEN_DATABASE

Legacy behavior is fully understood. Queries are documented. Response shape is known.

#### `POST /game_data/load/mission` - lines 653-676

- **Legacy behavior**:
  1. Reads `player_id` from request body
  2. Initializes PlayerProfile, queries player table
  3. Queries `player_missions` table: `SELECT mission_id,clear_count,clear_num,status,mission_status FROM player_missions WHERE player_id=$1`
  4. Returns `{missions: [{mission_id, clear_count, clear_num, status, mission_status}, ...]}`

- **Database tables READ**:
  - `player` (via initWithPlayerID)
  - `player_missions`

- **Database tables WRITTEN**: None

- **Expected response**:
  ```json
  {
    "missions": [
      {
        "mission_id": 136001,
        "clear_count": 0,
        "clear_num": 0,
        "status": 0,
        "mission_status": 0
      }
    ]
  }
  ```

- **Python implementation**: Returns 501 not_implemented
- **Parity status**: NOT IMPLEMENTED (intentional)

#### `POST /game_data/load` - lines 677-698

- **Legacy behavior**:
  1. Reads `player_id` from request body
  2. Initializes PlayerProfile, queries player table
  3. Queries `player_logins` for same_day_login_count, total_login_days
  4. Sets consecutive_login_days (faked: 1 if same_day_login_count > 0, else 0)
  5. Queries 14 additional tables (see below)
  6. Returns full game data structure

- **Database tables READ** (17 tables):
  - `player` (via initWithPlayerID)
  - `player_logins` (2 queries: same_day_login_count, total_login_days)
  - `player_buddies`
  - `player_progress`
  - `player_options`
  - `player_missions`
  - `player_buddy_win_poses`
  - `player_emblems`
  - `player_emblem_parts`
  - `player_titles`
  - `player_line_colors`
  - `player_mecha_sets`
  - `player_mecha_set_parts`
  - `player_mecha_colors`
  - `player_weapon_set`
  - `player_weapon_set_slots`
  - `player_side_weapons`

- **Database tables WRITTEN**: None

- **Computed fields**:
  - `violation_point`: hardcoded 0
  - `winning_streaks_2on2`: hardcoded 1
  - `buddy_skills`: hardcoded `[]`

- **Python implementation**: Returns 501 not_implemented
- **Parity status**: NOT IMPLEMENTED (intentional)

#### `POST /game_data/save` - lines 700-720

- **Legacy behavior**:
  1. Reads `player_id` from request body
  2. Iterates over all body keys
  3. For each recognized key, performs INSERT ON CONFLICT DO UPDATE
  4. Returns `{missions: [...], result: 1}` (missions re-queried after save)

- **Database tables WRITTEN** (15 tables + player scalar fields):
  - `player_options` (key: option_key, value: value_num)
  - `player_buddies` (key: buddy_id + buddy_key, value: buddy_value)
  - `player_progress` (key: progress_key, value: status)
  - `player_missions` (key: mission_id, values: clear_count, clear_num, status, mission_status)
  - `player_titles` (key: title_id, value: status)
  - `player_emblems` (key: emblem_id, 22 columns total)
  - `player_emblem_parts` (key: part_id, value: status)
  - `player_mecha_sets` (key: mecha_set_id, 11 columns total)
  - `player_mecha_set_parts` (key: mecha_set_id + part_id, values: mecha_id, design_id, color_id)
  - `player_buddy_win_poses` (key: buddy_id + win_pose_id, value: status)
  - `player_line_colors` (key: line_color_id, value: status)
  - `player_mecha_colors` (key: mecha_color_id, value: status)
  - `player_weapon_set` (key: weapon_set_id, values: use_count, use_time, status)
  - `player_weapon_set_slots` (key: weapon_set_id + slot_id, values: weapon_id, use_count, use_time)
  - `player_side_weapons` (key: side_weapon_id, values: use_count, use_time, status)
  - `player` (scalar UPDATE for: title_id_2on2, mecha_set_id, emblem_id_2on2, line_color_id_2on2, side_weapon_id, mecha_preset_id, rank_point, max_rank_id, rank_point_2on2, max_rank_id_2on2, buddy_id)

- **Database tables READ** (post-save):
  - `player_missions` (re-queried to return updated missions)

- **Handled body keys**: options, buddies, progresses, missions, titles, emblems, emblem_parts, mecha_sets, mecha_set_parts, buddy_win_poses, line_colors, mecha_colors, weapon_set, weapon_set_slots, side_weapons, title_id_2on2, mecha_set_id, emblem_id_2on2, line_color_id_2on2, side_weapon_id, mecha_preset_id, rank_point, max_rank_id, rank_point_2on2, max_rank_id_2on2, buddy_id, player_id

- **Unhandled keys**: Logged as "UNHANDLED DATA SAVE TYPE" with no action

- **Python implementation**: Returns 501 not_implemented
- **Parity status**: NOT IMPLEMENTED (intentional)

---

## Known Parity Gaps

### Critical Gaps (gameplay-affecting)

1. **game_data/load not implemented**
   - Client cannot load player progression, unlocks, or customizations
   - All game data queries return 501
   - Game will be non-functional without this

2. **game_data/save not implemented**
   - Client cannot persist player changes
   - All game data writes return 501
   - Progression will be lost between sessions

3. **game_data/load/mission not implemented**
   - Mission data cannot be loaded
   - Mission system non-functional

### Minor Gaps (cosmetic or secondary)

4. **consecutive_login_days faked in legacy**
   - Legacy: `consecutive_login_days = same_day_login_count ? 1 : 0`
   - This is a known limitation of the legacy implementation

5. **buddy_skills hardcoded to []**
   - Legacy line 151: `gameData.buddy_skills = []; // TODO`
   - Never implemented in legacy

6. **violation_point hardcoded to 0**
   - Legacy line 290: `gameData.violation_point = 0;`
   - Anti-cheat system was never implemented

7. **winning_streaks_2on2 hardcoded to 1**
   - Legacy line 291: `gameData.winning_streaks_2on2 = 1;`

### Missing Tables (referenced in code but no schema)

The following data types are referenced in `playerSaveGameData` or code comments but have no corresponding database table:

- `quests`
- `game_moneys`
- `present_items`
- `greetings`
- `buddy_greetings`
- `symbol_chats`
- `symbol_chat_slots`
- `cockpit_items`
- `mecha_presets`
- `mecha_preset_parts`
- `weapon_roles`
- `weapon_role_presets`
- `weapon_role_preset_slots`
- `weapons`

---

## Safe Source-PROVEN Subset

The following operations are fully documented and safe to implement:

### Load Operations (read-only, no side effects)

| Operation | Tables | Response Shape |
|-----------|--------|----------------|
| `game_data/load/mission` | player_missions | `{missions: [{mission_id, clear_count, clear_num, status, mission_status}]}` |
| `game_data/load` | 17 tables (see above) | Full game data object (see playerProfile.js:87-293) |

### Save Operations (INSERT ON CONFLICT DO UPDATE)

All save operations use the same pattern:
```sql
INSERT INTO table (player_id, ...) VALUES ($1, ...)
ON CONFLICT (player_id, key) DO UPDATE SET col = excluded.col
```

| Operation | Table | Conflict Key |
|-----------|-------|-------------|
| save options | player_options | (player_id, option_key) |
| save buddies | player_buddies | (player_id, buddy_id, buddy_key) |
| save progresses | player_progress | (player_id, progress_key) |
| save missions | player_missions | (player_id, mission_id) |
| save titles | player_titles | (player_id, title_id) |
| save emblems | player_emblems | (player_id, emblem_id) |
| save emblem_parts | player_emblem_parts | (player_id, part_id) |
| save mecha_sets | player_mecha_sets | (player_id, mecha_set_id) |
| save mecha_set_parts | player_mecha_set_parts | (player_id, mecha_set_id, part_id) |
| save buddy_win_poses | player_buddy_win_poses | (player_id, buddy_id, win_pose_id) |
| save line_colors | player_line_colors | (player_id, line_color_id) |
| save mecha_colors | player_mecha_colors | (player_id, mecha_color_id) |
| save weapon_set | player_weapon_set | (player_id, weapon_set_id) |
| save weapon_set_slots | player_weapon_set_slots | (player_id, weapon_set_id, slot_id) |
| save side_weapons | player_side_weapons | (player_id, side_weapon_id) |

Scalar player field updates:
```sql
UPDATE player SET field=$2 WHERE player_id=$1
```

Fields: title_id_2on2, mecha_set_id, emblem_id_2on2, line_color_id_2on2, side_weapon_id, mecha_preset_id, rank_point, max_rank_id, rank_point_2on2, max_rank_id_2on2, buddy_id

---

## Unknown / Ambiguous Behavior

### SOURCE_AMBIGUOUS

1. **Mission reward processing** (`/mission/reward/get`)
   - Legacy comment indicates expected response shape but no implementation exists
   - Reward logic, item grants, and mission completion are unimplemented

2. **Login bonus system** (`/player/login_bonus`)
   - Returns `{result: 1, login_bonuses: [], update_items: {}}`
   - Login bonus calculation logic is unknown

3. **Burst mode / matching** (protobuf handlers)
   - Complex state machine with room management
   - Partially implemented in Python via matching_service

### CAPTURE_REQUIRED

These behaviors exist in legacy but cannot be safely reimplemented without additional capture:

1. **Battle recording** (`/battle/record_2on2`)
   - Uses BattleRecorder class
   - Complex scoring and ranking logic
   - Must be preserved as controlled 501

2. **Player profile computation** (login stats)
   - Same-day login counting
   - Total login days
   - Consecutive login days (faked in legacy)

3. **Emblem structure assembly**
   - Complex nested object construction from flat DB columns
   - Multiple offset/scale/angle fields per design layer

---

## Implementation Priority

| Priority | Operation | Rationale |
|----------|-----------|-----------|
| P0 | game_data/load | Required for any client functionality |
| P0 | game_data/save | Required for progression persistence |
| P1 | game_data/load/mission | Required for mission system |
| P2 | /mission/reward/get | Requires reward logic design |
| P3 | /player/login_bonus | Requires bonus table/logic |
| N/A | /battle/record_2on2 | Preserve controlled 501 |
