# Starwing Paradox - Unknown Protocol Areas

> Classification of known, inferred, and unknown behaviors across HTTP and TCP/Protobuf protocols.

---

## 1. Confirmed Behavior (from source code)

### HTTP Endpoints

| Endpoint | Behavior | Evidence |
|----------|----------|----------|
| POST /version | Returns hardcoded version_main=70571, version_data=70571, stage_ids=[] | `starwing.js:407-426` |
| POST /resource | Returns raw c_resource.json contents | `starwing.js:779-789` |
| POST /matching/server | Returns matcher address, auto-authorizes IP via x-galaxy-real-ip | `starwing.js:345-369` |
| POST /matching/match_id/generate | Returns random int 10000-99999 as match_id | `starwing.js:428-438` |
| POST /ranking/national | Returns c_rankingNational.json | `starwing.js:458-460` |
| POST /ranking/location | Returns c_rankingStore.json | `starwing.js:462-464` |
| POST /ranking/prefecture | Returns c_rankingPrefecture.json | `starwing.js:466-468` |
| POST /ranking/event | Returns c_rankingEvent.json | `starwing.js:470-472` |
| POST /ranking/weapon | Returns c_rankingWeapon_r{role_id}.json, injects role_id | `starwing.js:474-479` |
| POST /player/profile/load | Loads player by nesys_id, auto-creates if not found | `starwing.js:488-507`, `playerProfile.js:26-73` |
| POST /player/login | Loads player by player_id, logs to player_logins, returns profile | `starwing.js:509-531`, `playerProfile.js:351-392` |
| POST /player/register | Updates player columns from request body, upserts progress | `starwing.js:557-574`, `playerProfile.js:394-436` |
| POST /game_data/load | Full game data load from 17+ tables | `starwing.js:677-698`, `playerProfile.js:87-296` |
| POST /game_data/load/mission | Mission-only data load | `starwing.js:653-676`, `playerProfile.js:74-86` |
| POST /game_data/save | Saves options, buddies, progresses, missions, titles, emblems, emblem_parts, mecha_sets, mecha_set_parts, buddy_win_poses, line_colors, mecha_colors, weapon_set, weapon_set_slots, side_weapons; updates player scalar fields | `starwing.js:700-720`, `playerProfile.js:438-722` |
| POST /battle/record_2on2 | Returns hardcoded battle rankings, reads missions for response | `starwing.js:739-759`, `battleRecorder.js:1-47` |

### TCP/Protobuf Handlers

| messageType | Name | Behavior | Evidence |
|-------------|------|----------|----------|
| 0x66 (102) | Ping | Echoes unixTimestamp with current server time | `starwing.js:118-123` |
| 200 | RequestEntryMatching | Responds with ResponseEntryMatching + NotifyMatchMade (fake VsCPU match) + NotifyMatchBegin | `starwing.js:222-294` |
| 208 | RequestEntryBurstGroup | Registers player for co-op, stores player data in memory, responds with timeout and max burst num | `burstMode.js:158-209` |
| 210 | RequestChangeBurstGroupMode | Creates new co-op room, adds owner, returns room info | `burstMode.js:110-157` |
| 214 | RequestUpdateBurstGroup | Lists all active rooms with owner info and player counts | `burstMode.js:94-108` |
| 216 | RequestBurstGroupSelect | Joins player to room, sends NotifyBurstGroupApply + NotifyBurstGroupUpdated to all members, then NotifyBurstMade | `burstMode.js:28-92` |

---

## 2. Strongly Inferred Behavior (from code comments, API-NOTES.txt)

### HTTP Endpoints

| Endpoint | Inferred Behavior | Evidence |
|----------|------------------|----------|
| POST /player/login_bonus | Should return daily login bonus items; expected fields: result, login_bonuses array, update_items | `starwing.js:534-554` returns stub `{result:1, login_bonuses:[], update_items:{}}` |
| POST /mission/reward/get | Should process mission reward claims; expected body: {player_id, mission_id, mission_reward_ids} | `API-NOTES.txt:8-10` shows captured request; `starwing.js:599` has TODO comment about expected response fields: intimacy_reward_ids, update_items, update_missions |
| POST /player/lock | Player account lock mechanism (possibly for cabinet handoff) | `API-NOTES.txt:51-63` shows captured request with body {player_id:10009} |
| POST /game_data/save (quests) | Should save quest progress; body contains JSON array of quest objects with quest_id, clear_count, clear_num1-3, status, quest_status | `API-NOTES.txt:4-5` shows captured quest data; `starwing.js:35` logs "Processing: quests" but no handler exists |

### TCP/Protobuf

| Behavior | Inferred | Evidence |
|----------|----------|----------|
| NotifyBurstMade (310) should be sent to room members when room is ready | Co-op start notification | `burstMode.js:73-83` sends to players[0] and players[1] |
| NotifyBurstMeets (311) is the "all players ready" notification | Match-ready state | `burstMode.js:85-90` (commented out) |
| NotifyBurstGroupUpdated (307) notifies all room members of player list changes | Room state sync | `burstMode.js:57-69` sends to all room members |

---

## 3. Unknown Behavior (missing from source)

### HTTP Endpoints

| Endpoint | What's Missing | Impact |
|----------|---------------|--------|
| POST /player/login_bonus | Actual bonus calculation logic, bonus item database, consecutive day tracking | Players receive no login rewards |
| POST /mission/reward/get | Mission reward processing, item granting, intimacy rewards | Players cannot claim mission rewards |
| POST /player/lock | Account locking mechanism | Unknown; possibly for multi-cabinet handoff |
| POST /credit/* | Credit/payment processing | All credit operations return empty object |
| POST /tutorial/* | Tutorial state management | Returns stub {result:1} |
| POST /battle/record_2on2 | Actual battle result processing, ranking computation, ELO/rating system | All battle results are faked |

### TCP/Protobuf

| Message | What's Missing | Impact |
|---------|---------------|--------|
| RequestCancelMatching (202) | Match cancellation handling | Cabinets cannot cancel matchmaking |
| RequestJoinMatching (206) | Join existing match handling | Cannot join in-progress matches |
| RequestIntrudeMatch | Match intrusion (late join) handling | Cannot join mid-match |
| RequestAssignMatch / ResponseAssignMatch | Server-side match assignment | No dedicated server orchestration |
| RequestEnterMatch / ResponseEnterMatch | Dedicated server match entry | No DS-based matchmaking |
| NotifyMatchEscape | Player disconnect from match | No graceful disconnect handling |
| NotifyMatchUpdated | Match state synchronization | No real-time match state updates |
| NotifyMatchBreak | Match termination | No match end processing |
| NotifyMatchClosed | Match closure | No match cleanup |
| NotifyMatchLeave | Player leaving match | No leave handling |
| NotifyMatchChangeState | Match state transitions | No state machine |
| NotifyMatchDiscontinue | Match discontinuation | No abort handling |
| NotifyEventMatchBreak | Event match termination | No event mode |
| NotifyBurstRejectPlayer | Kick player from room | No kick functionality |
| NotifyBurstMatchCancelled | Burst match cancellation | No burst cancellation |
| NotifyBurstMatchBreak | Burst match termination | No burst end processing |

---

## 4. Requires Packet Capture

The following areas need packet captures from a real arcade cabinet to understand the actual protocol:

| Area | What to Capture | Why |
|------|----------------|-----|
| Boot sequence | First HTTP requests on cabinet boot | Unknown initialization flow |
| Version negotiation | Full /version request/response | Unknown if additional fields are needed |
| Card scan flow | Requests after Banapassport scan | Unknown nesys_id discovery mechanism |
| Match flow (full) | Complete 100-yen match lifecycle | Only VsCPU fake match is implemented |
| Co-op flow (full) | Complete burst mode lifecycle | Room join/leave/disconnect edge cases |
| Mission reward flow | /mission/reward/get request/response | Unknown reward schema |
| Login bonus flow | /player/login_bonus request/response | Unknown bonus schema |
| Ranking update flow | How rankings are updated after battles | No ranking update mechanism |
| Error responses | Cabinet behavior on server errors | Unknown error handling protocol |
| Session management | How sessions are maintained across requests | sessionId field in PbMessage unused |
| Game data save triggers | When cabinet sends /game_data/save | Unknown save timing |

---

## 5. Requires Multi-Cabinet Validation

These behaviors involve interactions between multiple cabinets and cannot be validated with a single test setup:

| Area | What to Validate | Unknowns |
|------|-----------------|----------|
| 2v2 matchmaking | Two cabinets matching against each other | Team assignment, synchronization |
| Co-op burst mode | Two cabinets joining same room | Room state sync, player disconnect handling |
| Ranking system | Rankings shared across cabinets | Ranking update mechanism, cross-cabinet state |
| Match intrusions | Third cabinet joining in-progress match | Late join protocol, state synchronization |
| Event mode | Special event matches | Event rules, event state management |
| Dedicated server assignment | Multiple cabinets connecting to same DS | Load balancing, DS state reporting |
| Player migration | Player data consistency across cabinets | Race conditions, data conflicts |

---

## 6. Requires Official Server Captures

These areas likely require captures from the original (now-defunct) Bandai Namco servers:

| Area | Why |
|------|-----|
| Official ranking algorithm | How rankings are computed from battle results |
| Login bonus schedule | Daily/weekly/monthly bonus tables and rules |
| Mission reward tables | Reward item IDs and quantities per mission |
| Event configurations | Event rules, stages, and schedules |
| Dedicated server protocol | DS registration, state reporting, match assignment |
| Anti-cheat validation | How server validates battle results |
| Player data schema | Complete list of save data fields (many TODO comments in source) |
| Match timeout handling | How timeouts are enforced and timeouts expired |
| Credit integration | How real-money credits are processed |
| Version update flow | How version checks trigger client updates |
