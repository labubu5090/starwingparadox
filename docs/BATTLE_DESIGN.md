# Starwing Paradox - Battle System Design

> Audit date: 2026-08-25
> Status: Phase 1 — Forensic evidence collected, proposed architecture outlined

---

## 1. State Machine

```
CREATED ──> ASSIGNED ──> WAITING_READY ──> READY ──> RUNNING ──> RESULT_PENDING ──> COMPLETED
   │            │              │              │           │              │              │
   v            v              v              v           v              v              v
CANCELLED   DISCONNECTED   TIMED_OUT     DISCONNECTED  EXPIRED       FAILED        ARCHIVED
```

### State Definitions

| State | Description |
|-------|-------------|
| `CREATED` | Battle session record created |
| `ASSIGNED` | Battle assigned to players/cabinets |
| `WAITING_READY` | Waiting for all players to be ready |
| `READY` | All players confirmed ready |
| `RUNNING` | Battle in progress |
| `RESULT_PENDING` | Battle ended, waiting for result submission |
| `COMPLETED` | Results recorded, rewards distributed |
| `CANCELLED` | Battle cancelled before start |
| `DISCONNECTED` | Player connection lost during battle |
| `EXPIRED` | Battle timed out without completion |
| `FAILED` | System error during battle |

### Valid Transitions

| From | To | Trigger |
|------|----|---------|
| CREATED | ASSIGNED | Battle assigned to cabinets |
| CREATED | CANCELLED | Pre-battle cancellation |
| ASSIGNED | WAITING_READY | Cabinets connected |
| ASSIGNED | DISCONNECTED | Cabinet fails to connect |
| WAITING_READY | READY | All players confirm |
| WAITING_READY | TIMED_OUT | Ready timeout |
| WAITING_READY | DISCONNECTED | Player disconnects |
| READY | RUNNING | Battle starts |
| READY | CANCELLED | Pre-start cancellation |
| RUNNING | RESULT_PENDING | Battle ends (win/lose/draw) |
| RUNNING | EXPIRED | Battle exceeds time limit |
| RUNNING | DISCONNECTED | Player disconnects mid-battle |
| RESULT_PENDING | COMPLETED | Results recorded successfully |
| RESULT_PENDING | FAILED | Result recording error |
| COMPLETED | ARCHIVED | Results archived (optional) |

---

## 2. Legacy Evidence (PROVEN)

### 2.1 Battle Recorder — Hardcoded Responses

**File**: `legacy-js/js/starwing/battleRecorder.js:1-47`

The `battleRecord2on2` method returns **entirely hardcoded ranking values**:

```javascript
async battleRecord2on2(req_body){
    let response = new Object();

    response.winning_streaks_2on2 = 1;
    response.rank_point_2on2 = 10000;
    response.ranking_score_2on2 = 500;
    response.ranking_high_score_2on2 = 1000;
    response.gained_ranking_score_2on2 = 200;
    response.is_update_rank_point_2on2 = true;
    response.is_update_ranking_score_2on2 = true;
    response.is_up_ranking_score_2on2 = true;
    response.is_new_record_ranking_score_2on2 = true;

    // Hardcoded rewards
    response.update_items = { game_moneys: [{ game_money_id: 1, count: 50 }] };
    response.battle_reward_ids = [1];
    response.rank_up_reward_ids = [2];
    response.rank_point_reward_ids = [3];
    response.intimacy_up_reward_ids = [4];

    // Hardcoded avg score
    response.avg_minute_score = {
        stage_id: req_body.stage_id,
        rank_id: 1,
        avg_minute_score: 44
    };

    // Only this part is DB-backed
    let qtext = "SELECT mission_id,clear_count,clear_num,status,mission_status FROM player_missions WHERE player_id=$1";
    let res = await this.db.query(qtext, [req.body.player_id]);
    response.missions = res.rows;

    return response;
}
```

### 2.2 Battle Result Request Structure

**Source**: `legacy-js/js/starwing/API-NOTES.txt:15-16`

The cabinet sends a detailed battle result JSON:

```json
{
    "match_id": "41772",
    "player_id": "10009",
    "player_name": "ＮｏＮａｍｅ",
    "burst_group_id": "0",
    "mode_id": "33",
    "team_id": "0",
    "stage_id": "20001",
    "buddy": "{\"buddy_id\":5,\"skill_id1\":0,\"skill_id2\":0,\"skill_id3\":0}",
    "emblem": "{\"outline\":{...},\"main_design\":{...},\"sub_design\":{...}}",
    "battle_result": "win",
    "battle_time": "143",
    "play_time": "143",
    "matching_time": "0",
    "left_time": "37",
    "score_2on2": "{\"total\":13019,\"minute\":5463,\"is_win\":true,...}",
    "players_2on2": "[{\"player_id\":10009,...,\"battle_type\":\"beginning\",\"is_retire\":false,...}]",
    "detail_2on2": "{\"player\":{\"give_damage\":{...},\"take_damage\":{...},...}}"
}
```

### 2.3 Score Structure (score_2on2)

```json
{
    "total": 13019,
    "minute": 5463,
    "is_win": true,
    "diff_rank": 0,
    "is_change_player_count": true,
    "details": {
        "attack_damage": 2751,
        "attack_kill": 0,
        "attack_skill": 0,
        "support_heal": 0,
        "support_buff": 0,
        "support_debuff": 0,
        "support_burstgauge_damage": 4029,
        "high_risk_time": 1360,
        "high_risk_damaged": 0,
        "high_risk_death": -1000,
        "coop_disturbance": 0,
        "coop_cross_fire_damage": 50,
        "coop_cross_fire_support": 0,
        "coop_cross_burst_damage": 79,
        "coop_cross_burst_support": 500
    }
}
```

### 2.4 Player Detail Structure (players_2on2)

```json
[{
    "player_id": 10009,
    "player_name": "ＮｏＮａｍｅ",
    "burst_group_id": 0,
    "team_id": 0,
    "rank_id": 1,
    "total_score": 14019,
    "score_rank": 1,
    "play_time": 143,
    "buddy": { "buddy_id": 5, "skill_id1": 0, "skill_id2": 0, "skill_id3": 0 },
    "emblem": { "outline": {...}, "main_design": {...}, "sub_design": {...} },
    "battle_type": "beginning",
    "is_retire": false,
    "official_player_type_id": 0,
    "mecha_set_id": 101,
    "weapon_set_id": 100,
    "side_weapon_id": 2
}]
```

### 2.5 Battle Detail Structure (detail_2on2)

Contains per-weapon damage breakdown:
```json
{
    "player": {
        "give_damage": {
            "total": 2188,
            "weapons_2on2": [
                { "weapon_id": 1, "is_side_weapon": false, "type": 4, "total": 104 },
                { "weapon_id": 2, "is_side_weapon": false, "type": 4, "total": 0 },
                { "weapon_id": 63, "is_side_weapon": false, "type": 4, "total": 373 },
                { "weapon_id": 10011, "is_side_weapon": false, "type": 4, "total": ... }
            ]
        },
        "take_damage": { ... }
    }
}
```

### 2.6 Battle Result Response Structure

The server returns:

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
    "update_items": {
        "game_moneys": [{ "game_money_id": 1, "count": 50 }]
    },
    "battle_reward_ids": [1],
    "rank_up_reward_ids": [2],
    "rank_point_reward_ids": [3],
    "intimacy_up_reward_ids": [4],
    "avg_minute_score": {
        "stage_id": 20001,
        "rank_id": 1,
        "avg_minute_score": 44
    },
    "missions": [
        { "mission_id": 126001, "clear_count": 0, "clear_num": 133, "status": 0, "mission_status": 201 }
    ]
}
```

### 2.7 Key Observations

| Aspect | Evidence |
|--------|----------|
| **Only 2v2 recorded** | `battleRecord2on2` — no 1v1 handler exists |
| **Ranking hardcoded** | All ranking values are static, not computed |
| **No actual battle processing** | Server doesn't validate scores, just records |
| **Mission progress loaded from DB** | Only DB-backed part of the response |
| **Game money hardcoded** | Always 50 of type 1 |
| **No anti-cheat** | Scores accepted as-is from client |
| **No battle history table** | Results not persisted in PostgreSQL schema |

---

## 3. Proposed Architecture (PROPOSED)

### 3.1 Components

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Battle API  │────>│ Battle Sess  │────>│ Result Proc │
│  (HTTP)     │     │  Manager     │     │   Worker    │
└─────────────┘     └──────────────┘     └─────────────┘
       │                   │                    │
       │              ┌────┴────┐          ┌────┴────┐
       │              │ Battle  │          │ Ranking │
       │              │  State  │          │ Calc    │
       │              └─────────┘          └─────────┘
       │
  ┌────┴─────┐
  │  Battle  │  (result submission)
  │ Recorder │
  └──────────┘
```

### 3.2 New Database Tables (Proposed)

| Table | Purpose |
|-------|---------|
| `battle_sessions` | Battle lifecycle records |
| `battle_results` | Per-player battle results |
| `battle_scores` | Detailed score breakdowns |
| `battle_rewards` | Rewards distributed |
| `battle_history` | Historical battle records |
| `ranking_entries` | Player ranking state |
| `ranking_history` | Ranking point changes |

### 3.3 Battle Session Lifecycle

```
1. Match created → Battle session created (CREATED)
2. Players assigned → State: ASSIGNED
3. Players confirm ready → State: READY
4. Battle starts → State: RUNNING
5. Cabinet submits result → State: RESULT_PENDING
6. Server validates and records → State: COMPLETED
7. Rewards distributed, rankings updated
```

### 3.4 Result Validation Rules (Proposed)

| Rule | Description |
|------|-------------|
| Score bounds | Total score must be within reasonable range for battle duration |
| Duration check | Battle time must match play_time within tolerance |
| Weapon consistency | Referenced weapon IDs must exist in game data |
| Player consistency | All player IDs in result must be in the match |
| Anti-cheat | Detect impossible score patterns (e.g., damage > time * max_DPS) |
| Duplicate check | Prevent same match_id from being submitted twice |

### 3.5 Ranking Computation (Proposed)

**1v1 Ranking**:
- Points gained/lost based on rank difference between winner/loser
- Winning streaks provide bonus points
- Rank up/down thresholds at specific point values

**2v2 Ranking**:
- Team-based ranking with individual contribution weight
- Buddy intimacy increases with wins
- Separate rank tracks for 1v1 and 2v2

### 3.6 HTTP Battle Endpoints (Proposed)

| Endpoint | Purpose |
|----------|---------|
| `POST /battle/record_2on2` | Submit 2v2 battle result (legacy) |
| `POST /battle/record_1on1` | Submit 1v1 battle result (new) |
| `POST /battle/result` | Get battle result summary |
| `POST /battle/history` | Query battle history |
| `POST /battle/rewards/claim` | Claim battle rewards |

### 3.7 TCP Battle Messages (Proposed)

| messageType | Name | Direction |
|-------------|------|-----------|
| 400 | RequestBattleStart | Server→Client |
| 401 | ResponseBattleStart | Client→Server |
| 402 | NotifyBattleResult | Server→Client |
| 403 | RequestBattleResult | Client→Server |
| 404 | ResponseBattleResult | Server→Client |

---

## 4. Implementation Notes

### 4.1 Legacy Compatibility

The `POST /battle/record_2on2` endpoint must continue to work with the exact response format from the legacy server. The Python implementation should:

1. Accept the same request JSON structure
2. Return the same response JSON structure
3. Persist results to PostgreSQL (unlike legacy)
4. Compute rankings (unlike legacy hardcoded values)

### 4.2 Data Flow

```
Cabinet (UE4)
    │
    │── POST /battle/record_2on2 ──>  (HTTP)
    │   Body: { match_id, player_id, score_2on2, players_2on2, detail_2on2, ... }
    │
    │<── Response ─────────────────
    │   { rank_point_2on2, ranking_score_2on2, missions, update_items, ... }
    │
    │   [Server processes async]
    │   - Validates result
    │   - Updates player ranking
    │   - Updates mission progress
    │   - Distributes rewards
    │   - Records battle history
```

### 4.3 Score Computation

The client sends pre-computed scores. The server should:

1. **Validate** — Check for impossible values
2. **Store** — Persist raw scores for analytics
3. **Compute ranking delta** — Apply ranking formula
4. **Update missions** — Increment relevant mission counters
5. **Distribute rewards** — Game money, items, experience

### 4.4 Anti-Cheat Considerations

| Check | Description |
|-------|-------------|
| Score/duration ratio | Reject if avg_minute_score exceeds theoretical max |
| Weapon usage | Validate weapon_ids exist in game data |
| Player count | Ensure player count matches match configuration |
| Timestamp | Battle time should be reasonable (not 0, not 24h+) |
| Consistency | score_2on2.total should equal sum of player total_scores |

---

## 5. Open Questions

1. Does the client compute all scores, or does the server need to calculate any?
2. What is the actual ranking formula used by the original game?
3. Are there any 1v1 battle result captures available?
4. What triggers a rank up/down notification?
5. How are battle rewards determined — by stage, difficulty, or rank?
6. Is there a battle replay system, or only final results?
