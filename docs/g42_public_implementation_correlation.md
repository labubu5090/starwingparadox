# G42: Public Implementation Correlation Phase

## 1. Provenance

### ArcadeMachinist/StarwingParadox
- **URL**: https://github.com/ArcadeMachinist/StarwingParadox
- **Branch**: master
- **Language**: JavaScript (Express.js) + HTML + PostgreSQL
- **License**: Not confirmed (no LICENSE file found)
- **Description**: "Starwing Paradox Mock Server — WORK IN PROGRESS. Expect tons of dirty code, in-code experiments, debug print-outs."
- **Database**: PostgreSQL (user=paradox, host=localhost, database=paradox, port=5432)
- **Server**: Express.js on port 4001, nginx reverse proxy on port 80

### ArcadeMachinist/FakeNesicaService
- **URL**: https://github.com/ArcadeMachinist/FakeNesicaService
- **Branch**: master
- **Language**: C# (.NET 6)
- **License**: Not confirmed
- **Description**: Named-pipe server emulating NesysService for Starwing Paradox
- **Pipe name**: `nesys_games`

---

## 2. HTTP Route Inventory (starwing.js)

All routes are POST. Express app listens on port 4001.

| # | Path | Request Body | Response Body | DB Table |
|---|------|--------------|---------------|----------|
| 1 | `/matching/server` | *(none)* | `{"ip_addr":"host:port"}` | None |
| 2 | `/version` | *(none)* | `{"client_version":"70571","data_version":"70571","stage_ids":[]}` | None |
| 3 | `/matching/match_id/generate` | *(none)* | `{"match_id": N}` (random 10000-99999) | None |
| 4 | `/ranking/national` | *(none)* | Ranking data (from file) | File |
| 5 | `/ranking/location` | *(none)* | Ranking data (from file) | File |
| 6 | `/ranking/prefecture` | *(none)* | Ranking data (from file) | File |
| 7 | `/ranking/event` | *(none)* | Ranking data (from file) | File |
| 8 | `/ranking/weapon` | `role_id` | Weapon ranking (from file) | File |
| 9 | `/player/profile/load` | `nesys_id` | Full player profile | PostgreSQL |
| 10 | `/player/login` | `player_id`, `location_id`, `client_version`, `data_version` | Login data + progresses | PostgreSQL |
| 11 | `/player/login_bonus` | *(none)* | `{"result":1,"login_bonuses":[],"update_items":{}}` | None |
| 12 | `/player/register` | `player_id` + registration fields | `{"result":1}` | PostgreSQL |
| 13 | `/mission/*` | `player_id`, `mission_id`, `mission_reward_ids` | `{}` | None (stub) |
| 14 | `/credit/*` | *(none)* | `{}` | None (stub) |
| 15 | `/tutorial/*` | *(none)* | `{"result":1}` | None (stub) |
| 16 | `/game_data/load/mission` | `player_id` | Mission data | PostgreSQL |
| 17 | `/game_data/load` | `player_id` | Full game data (17 tables) | PostgreSQL |
| 18 | `/game_data/save` | `player_id` + save payload | `{"result":1,"missions":[...]}` | PostgreSQL |
| 19 | `/battle/record_2on2` | Full 2v2 battle record | Battle record response | PostgreSQL |
| 20 | `/resource` | *(none)* | Resource data (from file) | File |

### Common Response Headers
- `Content-type: application/json`
- `x-galaxy-api: */*`
- `x-galaxy-api-id: <echoed from request>`

### Catch-All Routes
- `/player/*` → `{"result":1}`
- `/game_data/*` → `{"result":1}`
- `/battle/*` → `{"result":1}`
- `/mock/*` → `{"ip_addr":"host:port"}`

---

## 3. Database Schema (paradox.sql)

### 17 PostgreSQL Tables

#### Core Player Table
**`player`** — 25 columns:
- `player_id` (integer, auto-increment)
- `nesys_id` (varchar(22))
- `player_name` (varchar(50), default 'ＮｏＮａｍｅ')
- `rank_id`, `rank_id_2on2` (integer, default 0)
- `title_id`, `title_id_2on2` (integer, default 0)
- `buddy_id` (smallint, default 0)
- `buddy_intimacy` (smallint, default 0)
- `line_color_id`, `line_color_id_2on2` (integer, default 0)
- `emblem_id`, `emblem_id_2on2` (integer, default 0)
- `birth_day`, `birth_month` (integer, default 1)
- `mecha_set_id`, `mecha_preset_id` (integer, default 0)
- `side_weapon_id` (integer, default 0)
- `rank_point`, `max_rank_id` (integer, default 0)
- `rank_point_2on2`, `max_rank_id_2on2` (integer, default 0)
- `violation_point` (integer, default 0)
- `ranking_pref_name`, `last_ranking_pref_name` (varchar(30), default '東京')
- `match_mode_id` (integer, default 0)

#### Key-Value Tables (extensible config)
- **`player_buddies`**: `player_id`, `buddy_id`, `buddy_key`, `buddy_value`
- **`player_options`**: `player_id`, `option_key`, `value_num`
- **`player_progress`**: `player_id`, `progress_key`, `status`

#### Collection Tables
- **`player_buddy_win_poses`**: `player_id`, `buddy_id`, `win_pose_id`, `status`
- **`player_mecha_colors`**: `player_id`, `mecha_color_id`, `status`
- **`player_emblem_parts`**: `player_id`, `part_id`, `status`
- **`player_emblems`**: `player_id`, `emblem_id` + 3 design layers (outline, main_design, sub_design) with offset, scale, angle
- **`player_line_colors`**: `player_id`, `line_color_id`, `status`
- **`player_titles`**: `player_id`, `title_id`, `status`
- **`player_side_weapons`**: `player_id`, `side_weapon_id`, `use_count`, `use_time`, `status`
- **`player_weapon_set`**: `player_id`, `weapon_set_id`, `use_count`, `use_time`, `status`
- **`player_weapon_set_slots`**: `player_id`, `weapon_set_id`, `slot_id`, `weapon_id`, `use_count`, `use_time`
- **`player_mecha_sets`**: `player_id`, `mecha_set_id`, `mecha_setbonus_id`, `weapon_set_id`, `is_decal`, `favorite`, `use_count`, `use_time`, `status`, `win_count`, `winning_streaks`
- **`player_mecha_set_parts`**: `player_id`, `mecha_set_id`, `part_id`, `mecha_id`, `design_id`, `color_id`
- **`player_missions`**: `player_id`, `mission_id`, `clear_count`, `clear_num`, `status`, `mission_status`
- **`player_logins`**: `player_id`, `ip_addr`, `location_id`, `client_version`, `data_version`, `ts_when`

---

## 4. playerProfile.js Analysis

### Initialization Methods
1. **`initWithPlayerID(db, player_id)`**: `SELECT * FROM player WHERE player_id=$1`
2. **`initWithNesys(db, nesys_id)`**: `SELECT * FROM player WHERE nesys_id=$1` → if not found, `INSERT INTO player(nesys_id) RETURNING player_id`

### Profile Load (`getProfile()`)
Returns player object with:
- Computed fields: `same_day_login_count`, `total_login_days`, `consecutive_login_days`
- Hardcoded: `last_pref_ranking_order_id=0`, `pref_ranking_top_player_count=0`, `official_player_type_id=0`
- Emblem object (3 layers: outline, main_design, sub_design)
- `progresses[]` from `player_progress`

### Login (`playerLogin(ip, req_body)`)
- Inserts into `player_logins`
- Returns: player + progresses + `greeting_ids=[1]` + `battle_count=3` + login stats + `burst_match=false` + `open_boss_matches=[20001]` + `next_boss_matches=[20002]`

### Game Data Load (`playerLoadGameData()`)
Returns object with:
- `player` (full player record + computed stats)
- `buddies[]` (from `player_buddies`, grouped by `buddy_id`)
- `progresses[]` (from `player_progress`)
- `options[]` (from `player_options`)
- `missions[]` (from `player_missions`)
- `buddy_skills[]` (TODO — empty)
- `buddy_win_poses[]` (from `player_buddy_win_poses`)
- `emblems[]` (from `player_emblems`, with 3-layer structure)
- `emblem_parts[]` (from `player_emblem_parts`)
- `titles[]` (from `player_titles`)
- `line_colors[]` (from `player_line_colors`)
- `mecha_sets[]` (from `player_mecha_sets`)
- `mecha_set_parts[]` (from `player_mecha_set_parts`)
- `mecha_colors[]` (from `player_mecha_colors`)
- `weapon_set[]` (from `player_weapon_set`)
- `weapon_set_slots[]` (from `player_weapon_set_slots`)
- `side_weapons[]` (from `player_side_weapons`)
- `violation_point=0`
- `winning_streaks_2on2=1`

### Game Data Save (`playerSaveGameData(req_body)`)
Handles 17 data types via `ON CONFLICT ... DO UPDATE`:
- `options`, `buddies`, `progresses`, `missions`, `titles`, `emblems`, `emblem_parts`
- `mecha_sets`, `mecha_set_parts`, `buddy_win_poses`, `line_colors`, `mecha_colors`
- `weapon_set`, `weapon_set_slots`, `side_weapons`
- Scalar fields: `title_id_2on2`, `mecha_set_id`, `emblem_id_2on2`, `line_color_id_2on2`, `side_weapon_id`, `mecha_preset_id`, `rank_point`, `max_rank_id`, `rank_point_2on2`, `max_rank_id_2on2`, `buddy_id`

### Player Register (`playerRegister(req_body)`)
- Updates `player` table with all fields
- Inserts/updates `player_progress` from `req_body.progresses`

---

## 5. battleRecorder.js Analysis

### Battle Record 2v2 (`battleRecord2on2(req_body)`)
Returns hardcoded response:
```json
{
  "winning_streaks_2on2": 1,
  "rank_point_2on2": 10000,
  "ranking_score_2on2": 500,
  "ranking_high_score_2on2": 1000,
  "gained_ranking_score_2on2": 200,
  "is_update_rank_point_2on2": true,
  "is_update_ranking_score_2on2": true,
  "is_up_ranking_score_2on2": true,
  "is_new_record_ranking_score_2on2": true,
  "update_items": {"game_moneys": [{"game_money_id": 1, "count": 50}]},
  "battle_reward_ids": [1],
  "rank_up_reward_ids": [2],
  "rank_point_reward_ids": [3],
  "intimacy_up_reward_ids": [4],
  "avg_minute_score": {"stage_id": ..., "rank_id": 1, "avg_minute_score": 44},
  "missions": [...]
}
```

---

## 6. FakeNesicaService Analysis

### Named Pipe Protocol
- **Pipe name**: `nesys_games`
- **Type**: `NamedPipeServerStream`, `PipeDirection.InOut`, `PipeTransmissionMode.Byte`
- **Security**: AuthenticatedUserSid with `ReadWrite | CreateNewInstance`
- **Threads**: 4 server threads running concurrently

### Binary Protocol
Each packet: **4-byte LE command ID** + optional payload.

**Client Commands** (NesysClientCommand enum):
- `LCOMMAND_CLIENT_START` (0x00)
- `LCOMMAND_CONNECT_REQUEST` (0x02)
- `LCOMMAND_DISCONNECT_REQUEST` (0x03)
- `LCOMMAND_GAME_START_REQUEST` (0x04)
- `LCOMMAND_GAME_END_REQUEST` (0x05)
- `LCOMMAND_GAME_CONTINUE_REQUEST` (0x06)
- `LCOMMAND_CARD_SELECT_REQUEST` (0x08)
- `LCOMMAND_CARD_INSERT_REQUEST` (0x0A)
- `LCOMMAND_CARD_UPDATE_REQUEST` (0x0B)
- `LCOMMAND_CARD_BUYS_ITEM_REQUEST` (0x0C)
- `LCOMMAND_CARD_TAKEOVER_REQUEST` (0x0D)
- `LCOMMAND_CARD_FORCE_TAKEOVER_REQ` (0x0E)
- `LCOMMAND_CARD_DECREASE_REQUEST` (0x0F)
- `LCOMMAND_CARD_REISSUE_TEST_REQUE` (0x10)
- `LCOMMAND_CARD_REISSUE_REQUEST` (0x11)
- `LCOMMAND_CARD_PLAYED_LIST_REQUES` (0x12)
- `LCOMMAND_RANKING_DATA_REQUEST` (0x13)
- `LCOMMAND_LOCALNW_INFO_REQUEST` (0x14)
- `LCOMMAND_GLOBALADDR_REQUEST` (0x15)
- `LCOMMAND_ECHO_REQUEST` (0x16)
- `LCOMMAND_ADAPTER_INFO_REQUEST` (0x17)
- `LCOMMAND_SERVICE_VERSION_REQUEST` (0x18)
- `LCOMMAND_DHCP_RENEW_REQUEST` (0x19)
- `LCOMMAND_GAMESTATUS_RESET_REQUEST` (0x24)
- `LCOMMAND_ROW_EVENTDATA_LIST_REQUEST` (0x24)
- `LCOMMAND_SET_INCOME_MODE_REQUEST` (0x20)
- `LCOMMAND_GAME_FREE_START_REQUEST` (0x27)
- `LCOMMAND_GAME_FREE_END_REQUEST` (0x28)

**Server reply** = client command + 0x100 (e.g., `LCOMMAND_CLIENT_START(0x00)` → `SCOMMAND_CLIENT_START_REPLY(0x10D)`)

### Data Returned to Game

| Command | Response Data |
|---------|---------------|
| `CLIENT_START` | Echo back + 8-byte reply |
| `CONNECT_REQUEST` | Reply + `SCOMMAND_NWRECOVER_NOTICE` + **`SCOMMAND_CERT_INIT_NOTICE`** containing: `TenpoId`, `TenpoName` (31 bytes), `Address` (33 bytes), `Ticket` (MD5 of gameid, 33 bytes), `Prefecture` (23 bytes), `ImgPath` (1024 bytes), `Host` string (relay_address, relay_port) |
| `LOCALNW_INFO_REQUEST` | Reply + `SCOMMAND_LOCALNW_INFO_NOTICE` containing: MAC address (16 bytes), IP addr (16 bytes), Gateway (16 bytes), DNS (16 bytes) — all ASCII strings padded to 16 bytes |
| `GLOBALADDR_REQUEST` | Returns `10.79.0.41` as global address |
| `SERVICE_VERSION_REQUEST` | Returns version string (e.g. `2.85(x64) 2014/07/08`) |
| `ADAPTER_INFO_REQUEST` | Returns network config: gateway `192.168.8.1`, IP `192.168.8.117`, mask `255.255.255.0`, DNS1/DNS2 `192.168.8.1`, MAC `001C42888475` |
| `ROW_EVENTDATA_LIST_REQUEST` | Returns 2112 zero bytes (empty event data) |
| `GAME_START/END/CONTINUE` | Standard game status reply |
| `INCOME_START/END/CONTINUE` | Standard income status reply |
| `GAME_FREE_END_REQUEST` | Returns `SCOMMAND_FREE_TICKET_REPLY` |
| `SET_INCOME_MODE_REQUEST` | Standard reply |
| `GAMESTATUS_RESET_REQUEST` | Standard reply |

### Card-Present Behavior
The pipe server handles card commands (`CARD_SELECT`, `CARD_INSERT`, `CARD_UPDATE`, `CARD_BUYS_ITEM`, `CARD_TAKEOVER`, `CARD_FORCE_TAKEOVER`, `CARD_DECREASE`, `CARD_REISSUE`, `CARD_PLAYED_LIST`) but these are **NOT implemented** — they fall through to the `default` case which simply echoes back the client's buffer unchanged.

### serverParams Struct
Configurable fields from the GUI:
- `s_gameid` — Game ID
- `s_tenpoid` — Shop/tenpo ID
- `s_tenponame` — Shop name
- `s_address` — Shop address
- `s_prefecture` — Prefecture
- `s_img` — News image path
- `s_version` — Version string
- `s_host` — Server host (relay address)
- `s_ticket` — MD5 of gameid (auto-generated)

---

## 7. Correlation with Live Evidence

### G41 Live Capture Findings
| Observation | Public Implementation | Correlation |
|-------------|----------------------|-------------|
| `/player/logout` URL rewritten to `api.example.com:8080/offline` | `/player/logout` NOT in starwing.js | **CONFIRMED**: Game client URL rewrite is hardcoded in binary, not from server config |
| `greetings=[]` and `buddy_greetings=[]` in logout request | `greeting_ids=[1]` in `playerLogin()`, `gameData.greetings = [] // TODO` | **PARTIAL**: Public impl has greeting_ids but no buddy_greetings |
| `/matching/server` (3 requests) caught by catch-all | `/matching/server` returns `{"ip_addr":"host:port"}` | **MATCH**: Route exists, returns TCP address |
| Zero tutorial/game_data/player routes triggered | `/tutorial/*` returns `{"result":1}` | **CONFIRMED**: Tutorial routes are stubs |
| `Result_Withdrawal` (not `Result_Timeover_Lose`) | Battle record returns hardcoded values | **PARTIAL**: Battle result is game-determined |
| `UserId:-1` throughout tutorial | `player_id` is auto-increment from PostgreSQL | **CONFIRMED**: No valid player_id during tutorial |
| Post-battle: `E_NoContinueBattleResult → E_BattleResult → E_Logout → TerminatedBattle → Title` | `/player/logout` URL rewritten | **CONFIRMED**: Logout flow bypasses our server |

### URL Rewrite Discovery
- **`api.example.com:8080`** is hardcoded in game client binary
- **NOT** from any server config or public implementation
- **NOT** found in starwing.js, nginx.vhost.conf, or any public repo
- **Conclusion**: Game client has built-in offline fallback URL for certain requests (like logout)

### NESYS Pipe vs HTTP
- **NESYS pipe** (`nesys_games`): Binary protocol for card operations, network config, game status
- **HTTP routes**: JSON API for player data, game data, battle records
- **Correlation**: Game uses pipe for card-present mode, HTTP for data sync
- **Security boundary**: We cannot emulate NESYS pipe (security boundary established in G29)

---

## 8. First Safe Vertical Slice

### Recommended: `/player/profile/load` + `/game_data/load` Implementation

**Rationale**:
1. These routes ARE triggered in card-present mode (after tutorial)
2. Public implementation provides complete reference
3. Safe (no NESYS pipe emulation required)
4. Testable with profile manager (card tap flow)

**Implementation Plan**:
1. **`/player/profile/load`**: Takes `nesys_id`, returns player profile
   - Query `local_profile` by UUID (nesys_id equivalent)
   - Return profile data in public implementation format
   - Handle new player creation (INSERT ON CONFLICT)

2. **`/game_data/load`**: Takes `player_id`, returns all game data
   - Query all 17 tables (or subset for MVP)
   - Return structured JSON matching public implementation format
   - Include computed fields (login counts, stats)

3. **`/game_data/save`**: Takes `player_id` + save payload
   - Upsert all data types via `ON CONFLICT ... DO UPDATE`
   - Return `{"result":1,"missions":[...]}`

4. **`/player/login`**: Takes `player_id`, returns login data
   - Insert into login history
   - Return player + progresses + greeting_ids + stats

### What NOT to Implement
- **NESYS pipe**: Security boundary (G29)
- **`/player/logout`**: URL rewritten by game client (G41 discovery)
- **Tutorial routes**: Never triggered during tutorial flow
- **Battle records**: Game-determined results
- **Ranking data**: Static files, low priority

---

## 9. Security Boundaries (DO NOT)

1. Do not force `bNesysServerLive` or `IsOnline`; do not patch the seven-flag gate
2. Do not implement LINKUP_NOTICE; do not fabricate NetworkInfo or certificate authentication
3. Do not patch executable, inject code, modify process memory, replay auth traffic
4. Do not identify local profile as NESiCA; do not fabricate player data
5. Do not create fake NESYS certificates; do not proxy cert3.nesys.jp or proxy.nesys.jp
6. Do not expose external interfaces — bind local tools to loopback only
7. Do not force tutorial completion or fabricate Result_Win
8. Do not replace UserId=-1 with invented positive ID
9. Do not claim in-game persistence if UserId=-1 prevents game save
10. Do not return generic success JSON without parser evidence

---

## 10. Key Takeaways

1. **Public implementation is a reference, not a specification** — it's a "WORK IN PROGRESS" with TODOs
2. **`api.example.com` is game-client hardcoded** — not from server config
3. **`/player/logout` is URL-rewritten** — never reaches our server
4. **Tutorial flow uses local storage** — no HTTP requests during tutorial
5. **Card-present mode triggers HTTP routes** — after tutorial completion
6. **NESYS pipe is separate from HTTP** — binary protocol for card operations
7. **17 PostgreSQL tables** in public impl → map to SQLite for our server
8. **Key-value pattern** for extensible config (buddies, options, progress)
9. **Battle records are hardcoded** in public impl — game-determined results
10. **First vertical slice**: `/player/profile/load` + `/game_data/load` (card-present mode)
