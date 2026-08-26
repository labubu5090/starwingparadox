# Starwing Paradox - HTTP Endpoint Matrix

> All endpoints are POST unless noted. Server: port 4001 (HTTP), port 6666 (TCP/Protobuf).
>
> **Audit date:** 2026-08-26

## Common Response Headers (all routes)

| Header | Value | Legacy evidence |
|--------|-------|----------------|
| Content-Type | application/json | `starwing.js:361` (all routes) |
| x-galaxy-api | `*/*` or route-specific | See per-route exceptions below |
| x-galaxy-api-id | Echoed from request header | `starwing.js:364` pattern |

**NOTE**: Python implementation uses `*/*` for ALL routes. Legacy JS uses route-specific values for 10 endpoints (documented below).

---

## Route Matrix

### Row 1: /version
- **Method**: POST
- **Path**: `/version`
- **Req Content-Type**: application/x-www-form-urlencoded or JSON
- **Req Codec**: JSON
- **Res Content-Type**: application/json
- **Res Codec**: JSON
- **Required Headers**: x-galaxy-api-id
- **DB Reads**: None
- **DB Writes**: None
- **Side Effects**: None
- **Legacy Status**: **VERIFIED_LEGACY_PARITY**
- **Evidence Location**: `starwing.js:407-426`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', '*/*');
  res.set('x-galaxy-api-id',req.header('x-galaxy-api-id'));
  res.send("{\n\t\"client_version\": \"" + version_main + "\",\n\t\"data_version\": \"" + version_data + "\",\n\t\"stage_ids\": []" + "}");
  ```
- **Python Target**: `/version` (`version.py:10-23`)
- **Python Returns**: `{"client_version":"70571","data_version":"70571","stage_ids":[]}`
- **LEGACY_COMPATIBILITY_MODE Effect**: None (always active)
- **Regression Tests**: Response has `client_version`, `data_version`, `stage_ids`

### Row 2: /resource
- **Method**: POST
- **Path**: `/resource`
- **Req Content-Type**: application/x-www-form-urlencoded or JSON
- **Req Codec**: JSON
- **Res Content-Type**: application/json
- **Res Codec**: JSON
- **Required Headers**: x-galaxy-api-id
- **DB Reads**: None (reads file `c_resource.json`)
- **DB Writes**: None
- **Side Effects**: None
- **Legacy Status**: **VERIFIED_LEGACY_PARITY**
- **Evidence Location**: `starwing.js:779-789`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', '*/*');
  res.set('x-galaxy-api-id',req.header('x-galaxy-api-id'));
  res.send(fs.readFileSync('starwing/c_resource.json','utf8'));
  ```
- **Python Target**: `/resource` (`resource.py:13-25`)
- **Python Returns**: `json.loads(RESOURCE_PATH.read_text())` — same file-based pattern
- **LEGACY_COMPATIBILITY_MODE Effect**: None (always active)
- **Regression Tests**: Returns raw JSON from c_resource.json

### Row 3: /matching/server
- **Method**: POST
- **Path**: `/matching/server`
- **Req Content-Type**: application/x-www-form-urlencoded or JSON
- **Req Codec**: JSON
- **Required Headers**: x-galaxy-api-id, x-galaxy-real-ip
- **DB Reads**: None
- **DB Writes**: None
- **Side Effects**: Legacy auto-authorizes client IP; Python does NOT
- **Legacy Status**: **LEGACY_STATIC_REIMPLEMENTED**
- **Evidence Location**: `starwing.js:345-369`
- **Legacy JS Code**:
  ```javascript
  if (req.header('x-galaxy-real-ip')) {
      if(authorizedClients.indexOf(req.header('x-galaxy-real-ip')) !== -1){
          console.log("Client IP " + req.header('x-galaxy-real-ip') + " already authorized");
      } else {
          authorizedClients.push(req.header('x-galaxy-real-ip'));
      }
  }
  res.set('x-galaxy-api', '*/*');
  res.send("{\n\t\"ip_addr\": \"" + matcher + "\"\n" + "}");
  ```
- **Python Target**: `/matching/server` (`matching.py:34-43`)
- **Python Returns (mode=true)**: `{"result":1,"servers":[]}` — **WRONG: missing `ip_addr`**
- **Python Returns (mode=false)**: HTTP 501
- **LEGACY_COMPATIBILITY_MODE Effect**: Mode=false→501. Mode=true→`{"result":1,"servers":[]}`
- **Gap**: Response shape differs (`ip_addr` vs `servers[]`). IP authorization side effect missing.
- **Regression Tests**: Response should have `ip_addr` field

### Row 4: /matching/match_id/generate
- **Method**: POST
- **Path**: `/matching/match_id/generate`
- **DB Reads**: None
- **DB Writes**: None
- **Legacy Status**: **LEGACY_STATIC_REIMPLEMENTED**
- **Evidence Location**: `starwing.js:428-438`
- **Legacy JS Code**:
  ```javascript
  let matchId = getRandomInt(10000,99999);
  res.send("{\"match_id\":"+matchId+"}");
  ```
- **Python Target**: `/matching/match_id/generate` (`matching.py:46-55`)
- **Python Returns (mode=true)**: `{"result":1,"match_id":""}` — **WRONG: empty string, not random int**
- **Python Returns (mode=false)**: HTTP 501
- **LEGACY_COMPATIBILITY_MODE Effect**: Mode=false→501. Mode=true→`{"result":1,"match_id":""}`
- **Gap**: match_id should be random integer 10000-99999

### Row 5: /matching/* (fallback)
- **Method**: POST
- **Path**: `/matching/*`
- **Legacy Status**: **LEGACY_STATIC_REIMPLEMENTED**
- **Evidence Location**: `starwing.js:440-449`
- **Legacy JS Code**: `res.send("{}")`
- **Python Returns (mode=true)**: `{"result":1}` — **WRONG: should be `{}`**
- **Gap**: Legacy returns empty `{}`, Python returns `{"result":1}`

### Row 6: /ranking/national
- **Method**: POST
- **Path**: `/ranking/national`
- **Legacy Status**: **LEGACY_STATIC_REIMPLEMENTED**
- **Evidence Location**: `starwing.js:458-460`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', 'ranking/national');
  res.send(fs.readFileSync('starwing/c_rankingNational.json','utf8'));
  ```
- **Python Returns (mode=true)**: `{"result":1,"ranking":[]}` — **WRONG: empty array, no file read**
- **Gap**: Missing actual ranking JSON data. Wrong `x-galaxy-api` header (`*/\*` vs `ranking/national`)

### Row 7: /ranking/location
- **Method**: POST
- **Path**: `/ranking/location`
- **Legacy Status**: **LEGACY_STATIC_REIMPLEMENTED**
- **Evidence Location**: `starwing.js:462-464`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', 'ranking/location');
  res.send(fs.readFileSync('starwing/c_rankingStore.json','utf8'));
  ```
- **Python Returns (mode=true)**: `{"result":1,"ranking":[]}` — **WRONG**
- **Gap**: Same as /ranking/national

### Row 8: /ranking/prefecture
- **Method**: POST
- **Path**: `/ranking/prefecture`
- **Legacy Status**: **LEGACY_STATIC_REIMPLEMENTED**
- **Evidence Location**: `starwing.js:466-468`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', 'ranking/prefecture');
  res.send(fs.readFileSync('starwing/c_rankingPrefecture.json','utf8'));
  ```
- **Python Returns (mode=true)**: `{"result":1,"ranking":[]}` — **WRONG**

### Row 9: /ranking/event
- **Method**: POST
- **Path**: `/ranking/event`
- **Legacy Status**: **LEGACY_STATIC_REIMPLEMENTED**
- **Evidence Location**: `starwing.js:470-472`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', 'ranking/event');
  res.send(fs.readFileSync('starwing/c_rankingEvent.json','utf8'));
  ```
- **Python Returns (mode=true)**: `{"result":1,"ranking":[]}` — **WRONG**

### Row 10: /ranking/weapon
- **Method**: POST
- **Path**: `/ranking/weapon`
- **Legacy Status**: **LEGACY_STATIC_REIMPLEMENTED**
- **Evidence Location**: `starwing.js:474-479`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', 'ranking/event');  // BUG: should be 'ranking/weapon'
  let jWeapons = JSON.parse(fs.readFileSync('starwing/c_rankingWeapon_r'+req.body.role_id+'.json','utf8'));
  jWeapons.role_id = req.body.role_id;
  res.send(JSON.stringify(jWeapons,null,4));
  ```
- **Python Returns (mode=true)**: `{"result":1,"ranking":[]}` — **WRONG**
- **Gap**: No file read, no `role_id` parameter processing

### Row 11: /ranking/* (fallback)
- **Method**: POST
- **Path**: `/ranking/*`
- **Legacy Status**: **LEGACY_STATIC_REIMPLEMENTED**
- **Evidence Location**: `starwing.js:481-485`
- **Legacy JS Code**: `res.send("{}")` (note: `deafult` typo means default case never runs)
- **Python Returns (mode=true)**: `{"result":1}` — **WRONG: should be `{}`**

### Row 12: /player/profile/load
- **Method**: POST
- **Path**: `/player/profile/load`
- **DB Reads**: player, player_logins, player_progress
- **DB Writes**: INSERT into player (auto-create if nesys_id not found)
- **Legacy Status**: **LEGACY_DB_BEHAVIOR_PARTIAL**
- **Evidence Location**: `starwing.js:488-507`, `playerProfile.js:26-73`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', 'player/profile');
  let pt = new pp.PlayerProfile();
  await pt.initWithNesys(pgdb,req.body.nesys_id);
  res.send(JSON.stringify(await pt.getProfile()));
  ```
- **Python Target**: `/player/profile/load` (`player.py:38-76`)
- **Python Returns**: DB query → `_ok(player_id=..., name=..., level=..., exp=..., gold=..., jewels=..., progresses=[], items=[])`
- **LEGACY_COMPATIBILITY_MODE Effect**: None (always active)
- **Gap**: Python missing `emblem`, `same_day_login_count`, `total_login_days`, `consecutive_login_days`, `last_pref_ranking_order_id`, `pref_ranking_top_player_count`, `official_player_type_id`. Python adds `gold`/`jewels` not in legacy.
- **Regression Tests**: Profile response schema; auto-create behavior

### Row 13: /player/login
- **Method**: POST
- **Path**: `/player/login`
- **DB Reads**: player, player_logins, player_progress
- **DB Writes**: INSERT into player_logins
- **Legacy Status**: **LEGACY_DB_BEHAVIOR_PARTIAL**
- **Evidence Location**: `starwing.js:509-531`, `playerProfile.js:351-392`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', 'player/login');
  let pt = new pp.PlayerProfile();
  await pt.initWithPlayerID(pgdb,req.body.player_id);
  res.send(JSON.stringify(await pt.playerLogin(req.header('x-galaxy-real-ip'),req.body)));
  ```
- **Python Returns**: DB update → `_ok(player_id=..., progresses=[], login_bonuses=[])`
- **LEGACY_COMPATIBILITY_MODE Effect**: None (always active)
- **Gap**: Python missing `greeting_ids`, `battle_count`, `same_day_login_count`, `total_login_days`, `consecutive_login_days`, `burst_match`, `open_boss_matches`, `next_boss_matches`. Python adds `login_bonuses` not in legacy login response.

### Row 14: /player/login_bonus
- **Method**: POST
- **Path**: `/player/login_bonus`
- **DB Reads**: None
- **DB Writes**: None
- **Legacy Status**: **VERIFIED_LEGACY_PARITY** (when mode=true)
- **Evidence Location**: `starwing.js:534-554`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', 'player/login');
  res.send("{\n\"result\": 1, " + "\"login_bonuses\": []," + "\"update_items\": {}" + "}");
  ```
- **Python Target**: `/player/login_bonus` (`player.py:110-121`)
- **Python Returns (mode=true)**: `{"result":1,"login_bonuses":[],"update_items":{}}`
- **Python Returns (mode=false)**: HTTP 501
- **LEGACY_COMPATIBILITY_MODE Effect**: Gated. Matches legacy when `true`.
- **Note**: Legacy sets `x-galaxy-api: player/login` (not `*/\*`). Python uses `*/\*`.

### Row 15: /player/register
- **Method**: POST
- **Path**: `/player/register`
- **DB Reads**: player
- **DB Writes**: UPDATE player, UPSERT player_progress
- **Legacy Status**: **LEGACY_DB_BEHAVIOR_PARTIAL**
- **Evidence Location**: `starwing.js:557-574`, `playerProfile.js:394-436`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', 'player/register');
  let pt = new pp.PlayerProfile();
  await pt.initWithPlayerID(pgdb,req.body.player_id);
  await pt.playerRegister(req.body);
  res.send("{\n\"result\": 1" + "}");
  ```
- **Python Returns**: DB write → `_ok(player_id="", name=..., level=1, exp=0, gold=0, jewels=0)`
- **Gap**: Legacy returns ONLY `{"result":1}`. Python returns extra fields.

### Row 16: /player/* (fallback)
- **Method**: POST
- **Path**: `/player/*`
- **Legacy Status**: **VERIFIED_LEGACY_PARITY** (when mode=true)
- **Evidence Location**: `starwing.js:576-592`
- **Legacy JS Code**: `res.send("{\n\"result\": 1\n}")`
- **Python Returns (mode=true)**: `{"result":1}` ✓
- **Python Returns (mode=false)**: HTTP 501

### Row 17: /game_data/load/mission
- **Method**: POST
- **Path**: `/game_data/load/mission`
- **DB Reads**: player_missions
- **DB Writes**: None
- **Legacy Status**: **LEGACY_DB_BEHAVIOR_PARTIAL**
- **Evidence Location**: `starwing.js:653-676`, `playerProfile.js:74-86`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', 'game_data/load');
  let pt = new pp.PlayerProfile();
  await pt.initWithPlayerID(pgdb,req.body.player_id);
  let pgd = await pt.playerLoadGameDataMissions();
  res.send(JSON.stringify(pgd,0,4));
  ```
- **Python Returns (mode=true)**: `{"result":1,"missions":[]}` — **WRONG: no DB query**
- **Gap**: Legacy queries `player_missions` table and returns actual data

### Row 18: /game_data/load
- **Method**: POST
- **Path**: `/game_data/load`
- **DB Reads**: player, player_logins, player_buddies, player_progress, player_options, player_missions, player_buddy_win_poses, player_emblems, player_emblem_parts, player_titles, player_line_colors, player_mecha_sets, player_mecha_set_parts, player_mecha_colors, player_weapon_set, player_weapon_set_slots, player_side_weapons
- **DB Writes**: None
- **Legacy Status**: **LEGACY_DB_BEHAVIOR_PARTIAL**
- **Evidence Location**: `starwing.js:677-698`, `playerProfile.js:87-296`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', 'game_data/load');
  let pt = new pp.PlayerProfile();
  await pt.initWithPlayerID(pgdb,req.body.player_id);
  let pgd = await pt.playerLoadGameData();
  res.send(JSON.stringify(pgd,0,4));
  ```
- **Python Returns (mode=true)**: `{"result":1,"game_data":{}}` — **WRONG: no DB query, empty object**
- **Gap**: Legacy performs 15+ DB queries and returns comprehensive game state

### Row 19: /game_data/save
- **Method**: POST
- **Path**: `/game_data/save`
- **DB Reads**: player_missions (for response)
- **DB Writes**: UPSERT into 15+ tables; UPDATE player
- **Legacy Status**: **LEGACY_DB_BEHAVIOR_PARTIAL**
- **Evidence Location**: `starwing.js:700-720`, `playerProfile.js:438-722`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', 'game_data/save');
  let pt = new pp.PlayerProfile();
  await pt.initWithPlayerID(pgdb,req.body.player_id);
  let gd = await pt.playerSaveGameData(req.body);
  res.send(JSON.stringify(gd,0,4));
  ```
- **Python Returns (mode=true)**: `{"result":1}` — **WRONG: no DB writes, wrong response shape**
- **Gap**: Legacy performs massive UPSERT operation; response includes `{result:1, missions:[...]}`

### Row 20: /game_data/* (fallback)
- **Method**: POST
- **Path**: `/game_data/*`
- **Legacy Status**: **VERIFIED_LEGACY_PARITY** (when mode=true)
- **Evidence Location**: `starwing.js:722-738`
- **Legacy JS Code**: `res.send("{\n\"result\": 1\n}")`
- **Python Returns (mode=true)**: `{"result":1}` ✓

### Row 21: /battle/record_2on2
- **Method**: POST
- **Path**: `/battle/record_2on2`
- **DB Reads**: player_missions
- **DB Writes**: None (battle results not persisted)
- **Legacy Status**: **LEGACY_DB_BEHAVIOR_PARTIAL**
- **Evidence Location**: `starwing.js:739-759`, `battleRecorder.js:1-47`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', '*/*');
  let myBr = new br.BattleRecorder(pgdb);
  let response = await myBr.battleRecord2on2(req.body);
  res.send(JSON.stringify(response,0,4));
  ```
- **Legacy response** (from `battleRecorder.js:5-43`):
  ```javascript
  { winning_streaks_2on2: 1, rank_point_2on2: 10000,
    ranking_score_2on2: 500, ranking_high_score_2on2: 1000,
    gained_ranking_score_2on2: 200, ...,
    update_items: { game_moneys: [{game_money_id:1, count:50}] },
    battle_reward_ids: [1], rank_up_reward_ids: [2], ...,
    missions: [...] }
  ```
- **Python Returns (mode=true)**: `{"result":1}` — **WRONG: completely different shape**
- **Gap**: Legacy returns complex object with ranking data, rewards, missions. Python returns `{result:1}`.

### Row 22: /battle/* (fallback)
- **Method**: POST
- **Path**: `/battle/*`
- **Legacy Status**: **VERIFIED_LEGACY_PARITY** (when mode=true)
- **Evidence Location**: `starwing.js:761-777`
- **Legacy JS Code**: `res.send("{\n\"result\": 1\n}")`
- **Python Returns (mode=true)**: `{"result":1}` ✓

### Row 23: /mission/* (fallback)
- **Method**: POST
- **Path**: `/mission/*`
- **Legacy Status**: **VERIFIED_LEGACY_PARITY** (when mode=true)
- **Evidence Location**: `starwing.js:595-614`
- **Legacy JS Code**: `res.send("{\n}")` → returns `{}`
- **Python Returns (mode=true)**: `{}` ✓
- **LEGACY_COMPATIBILITY_MODE Effect**: Mode=false→501. Mode=true→`{}`
- **Note**: Known sub-route `/mission/reward/get` with body schema in API-NOTES.txt

### Row 24: /credit/* (fallback)
- **Method**: POST
- **Path**: `/credit/*`
- **Legacy Status**: **VERIFIED_LEGACY_PARITY** (when mode=true)
- **Evidence Location**: `starwing.js:616-631`
- **Legacy JS Code**: `res.send("{\n}")` → returns `{}`
- **Python Returns (mode=true)**: `{}` ✓

### Row 25: /tutorial/* (fallback)
- **Method**: POST
- **Path**: `/tutorial/*`
- **Legacy Status**: **VERIFIED_LEGACY_PARITY** (when mode=true)
- **Evidence Location**: `starwing.js:634-650`
- **Legacy JS Code**: `res.send("{\n\"result\": 1\n}")` → returns `{"result":1}`
- **Python Returns (mode=true)**: `{"result":1}` ✓

### Row 26: /mock/matching/server
- **Method**: POST
- **Path**: `/mock/matching/server`
- **Legacy Status**: **CONTROLLED_NOT_IMPLEMENTED**
- **Evidence Location**: `starwing.js:371-387`
- **Legacy JS Code**:
  ```javascript
  res.set('x-galaxy-api', '*/*');
  res.send("{\n\t\"ip_addr\": \"" + matcher + "\"\n" + "}");
  ```
- **Python Target**: None (no `/mock` route in Python)

### Row 27: /mock/* (fallback)
- **Method**: POST
- **Path**: `/mock/*`
- **Legacy Status**: **CONTROLLED_NOT_IMPLEMENTED**
- **Evidence Location**: `starwing.js:389-405`
- **Legacy JS Code**: Same as `/mock/matching/server`

### Row 28: GET /health
- **Method**: GET
- **Path**: `/health`
- **Legacy Status**: **SYNTHETIC_FOUNDATION_ONLY**
- **Python Returns**: `{"status":"ok"}`

### Row 29: GET /ready
- **Method**: GET
- **Path**: `/ready`
- **Legacy Status**: **SYNTHETIC_FOUNDATION_ONLY**
- **Python Returns**: `{"status":"ready","database":"ok"}` or `{"status":"not ready","database":"error"}`

---

## LEGACY_COMPATIBILITY_MODE Matrix

### Setting: `true` (default)

| Route | Status | Headers | Body |
|-------|--------|---------|------|
| /player/login_bonus | 200 | `x-galaxy-api: */*` | `{"result":1,"login_bonuses":[],"update_items":{}}` |
| /player/{fallback} | 200 | `x-galaxy-api: */*` | `{"result":1}` |
| /matching/server | 200 | `x-galaxy-api: */*` | `{"result":1,"servers":[]}` |
| /matching/match_id/generate | 200 | `x-galaxy-api: */*` | `{"result":1,"match_id":""}` |
| /matching/{fallback} | 200 | `x-galaxy-api: */*` | `{"result":1}` |
| /ranking/national | 200 | `x-galaxy-api: */*` | `{"result":1,"ranking":[]}` |
| /ranking/location | 200 | `x-galaxy-api: */*` | `{"result":1,"ranking":[]}` |
| /ranking/prefecture | 200 | `x-galaxy-api: */*` | `{"result":1,"ranking":[]}` |
| /ranking/event | 200 | `x-galaxy-api: */*` | `{"result":1,"ranking":[]}` |
| /ranking/weapon | 200 | `x-galaxy-api: */*` | `{"result":1,"ranking":[]}` |
| /ranking/{fallback} | 200 | `x-galaxy-api: */*` | `{"result":1}` |
| /game_data/load | 200 | `x-galaxy-api: */*` | `{"result":1,"game_data":{}}` |
| /game_data/load/mission | 200 | `x-galaxy-api: */*` | `{"result":1,"missions":[]}` |
| /game_data/save | 200 | `x-galaxy-api: */*` | `{"result":1}` |
| /game_data/{fallback} | 200 | `x-galaxy-api: */*` | `{"result":1}` |
| /battle/record_2on2 | 200 | `x-galaxy-api: */*` | `{"result":1}` |
| /battle/{fallback} | 200 | `x-galaxy-api: */*` | `{"result":1}` |
| /mission/{fallback} | 200 | `x-galaxy-api: */*` | `{}` |
| /credit/{fallback} | 200 | `x-galaxy-api: */*` | `{}` |
| /tutorial/{fallback} | 200 | `x-galaxy-api: */*` | `{"result":1}` |

### Setting: `false`

| Route | Status | Headers | Body |
|-------|--------|---------|------|
| /player/login_bonus | **501** | `x-galaxy-api: */*` | `{"error":"not_implemented","endpoint":"/player/login_bonus","corrid":"..."}` |
| /player/{fallback} | **501** | `x-galaxy-api: */*` | `{"error":"not_implemented","endpoint":"/player/...","corrid":"..."}` |
| /matching/server | **501** | `x-galaxy-api: */*` | `{"error":"not_implemented",...}` |
| /matching/match_id/generate | **501** | `x-galaxy-api: */*` | `{"error":"not_implemented",...}` |
| /matching/{fallback} | **501** | `x-galaxy-api: */*` | `{"error":"not_implemented",...}` |
| /ranking/* (all) | **501** | `x-galaxy-api: */*` | `{"error":"not_implemented",...}` |
| /game_data/* (all) | **501** | `x-galaxy-api: */*` | `{"error":"not_implemented",...}` |
| /battle/* (all) | **501** | `x-galaxy-api: */*` | `{"error":"not_implemented",...}` |
| /mission/{fallback} | **501** | `x-galaxy-api: */*` | `{"error":"not_implemented",...}` |
| /credit/{fallback} | **501** | `x-galaxy-api: */*` | `{"error":"not_implemented",...}` |
| /tutorial/{fallback} | **501** | `x-galaxy-api: */*` | `{"error":"not_implemented",...}` |

### Setting: Absent (env var unset)

Behavior is identical to `true` — Pydantic `Settings` class defaults `legacy_compatibility_mode` to `True`.

### Invalid values

Pydantic `BaseSettings` with `bool` type will:
- `"true"` / `"True"` / `"1"` / `"yes"` → `True`
- `"false"` / `"False"` / `"0"` / `"no"` → `False`
- Non-parseable strings → Pydantic `ValidationError` at startup
- Missing env var → uses default `True`

---

## Endpoints NOT Gated by LEGACY_COMPATIBILITY_MODE

These endpoints always return real data regardless of mode:

| Route | File | Always Active |
|-------|------|---------------|
| POST /player/profile/load | `player.py:38` | ✓ |
| POST /player/login | `player.py:79` | ✓ |
| POST /player/register | `player.py:124` | ✓ |
| POST /version | `version.py:10` | ✓ |
| POST /resource | `resource.py:13` | ✓ |
| GET /health | `health.py:11` | ✓ |
| GET /ready | `health.py:16` | ✓ |

---

## Classification Definitions

| Classification | Meaning |
|----------------|---------|
| **VERIFIED_LEGACY_PARITY** | Response shape, status, and headers match legacy JS (with mode=true where gated) |
| **LEGACY_DB_BEHAVIOR_PARTIAL** | Endpoint performs DB operations but response shape differs from legacy |
| **LEGACY_STATIC_REIMPLEMENTED** | Legacy serves static data (JSON files/fixed strings); Python returns different shape |
| **SYNTHETIC_FOUNDATION_ONLY** | No legacy equivalent; infrastructure endpoint |
| **CONTROLLED_NOT_IMPLEMENTED** | Legacy has route; Python deliberately omits it |
| **ROUTE_WITHOUT_SOURCE_EVIDENCE** | Route exists in Python but no legacy JS evidence found |
| **UNKNOWN** | Insufficient evidence to classify |
