# Starwing Paradox - Matching System Design

> Audit date: 2026-08-25
> Status: Phase 1 — Forensic evidence collected, proposed architecture outlined

---

## 1. State Machine

```
CREATED ──> QUEUED ──> CANDIDATE_FOUND ──> ROOM_CREATED ──> WAITING_READY ──> READY ──> BATTLE_ASSIGNED
   │            │              │                 │                │              │            │
   │            │              │                 │                │              │            │
   v            v              v                 v                v              v            v
CANCELLED   TIMED_OUT     DISCONNECTED      FAILED           CANCELLED     DISCONNECTED   COMPLETED
```

### State Definitions

| State | Description |
|-------|-------------|
| `CREATED` | Match request received, not yet queued |
| `QUEUED` | Player waiting in matchmaking pool |
| `CANDIDATE_FOUND` | Potential match partners identified |
| `ROOM_CREATED` | Dedicated server room allocated |
| `WAITING_READY` | Waiting for all players to confirm ready |
| `READY` | All players confirmed, battle can begin |
| `BATTLE_ASSIGNED` | Battle session started, cabinets notified |
| `CANCELLED` | Player or system cancelled the match |
| `TIMED_OUT` | Matchmaking exceeded timeout window |
| `DISCONNECTED` | Player connection lost during matching |
| `FAILED` | System error prevented match completion |

### Valid Transitions

| From | To | Trigger |
|------|----|---------|
| CREATED | QUEUED | RequestEntryMatching accepted |
| CREATED | CANCELLED | Player cancels before queue |
| QUEUED | CANDIDATE_FOUND | Matchmaker finds compatible players |
| QUEUED | TIMED_OUT | Queue timeout expires |
| QUEUED | CANCELLED | Player cancels while queued |
| QUEUED | DISCONNECTED | Player TCP disconnect |
| CANDIDATE_FOUND | ROOM_CREATED | Dedicated server allocated |
| CANDIDATE_FOUND | DISCONNECTED | Player TCP disconnect |
| CANDIDATE_FOUND | FAILED | No server available |
| ROOM_CREATED | WAITING_READY | Room ready for players |
| ROOM_CREATED | FAILED | Server allocation failed |
| WAITING_READY | READY | All players send ready signal |
| WAITING_READY | TIMED_OUT | Ready confirmation timeout |
| WAITING_READY | DISCONNECTED | Player TCP disconnect |
| WAITING_READY | CANCELLED | Player cancels ready |
| READY | BATTLE_ASSIGNED | Battle session launched |
| READY | DISCONNECTED | Player TCP disconnect |
| BATTLE_ASSIGNED | COMPLETED | Battle ends normally |
| BATTLE_ASSIGNED | DISCONNECTED | Player TCP disconnect mid-battle |

---

## 2. Legacy Evidence (PROVEN)

### 2.1 HTTP Matching Server Endpoint

**File**: `legacy-js/js/starwing.js:345-368`

The only HTTP matching endpoint that works is `POST /matching/server`. It:
1. Reads `x-galaxy-real-ip` from the Nginx-injected header
2. Adds the IP to an in-memory `authorizedClients` whitelist
3. Returns the matcher address: `{ "ip_addr": "paradox.yourdomain.com:6666" }`

This is the **bootstrapping step** — the cabinet needs this to know where to TCP-connect.

```javascript
// starwing.js:352-358
if (req.header('x-galaxy-real-ip')) {
    if(authorizedClients.indexOf(req.header('x-galaxy-real-ip')) !== -1){
        console.log("Client IP " + req.header('x-galaxy-real-ip') + " already authorized");
    } else {
        authorizedClients.push(req.header('x-galaxy-real-ip'));
    }
}
```

### 2.2 TCP Match Entry (messageType 200)

**File**: `legacy-js/js/starwing.js:222-294`

The `RequestEntryMatching` handler (messageType 200) is the core matching flow. It executes a **hardcoded single-player VS CPU match**:

**Step 1**: Respond with `ResponseEntryMatching` (201)
```javascript
payload = {
    packetId: decoded.packetId,
    messageType: 201,
    ResponseEntryMatching: { messageId: 1, timeout: 45 }
};
```

**Step 2**: Send fake `NotifyMatchMade` (302) with hardcoded data
```javascript
payload = {
    packetId: parseInt(decoded.packetId)+1,
    messageType: 302,
    NotifyMatchMade: {
        Match: {
            Team: [{
                PlayerCount: 2,
                Player: [
                    { PlayerId: 10010, PlayerName: "ArcadeMachinist", PlayerRank: 20, ... },
                    { PlayerId: 10011, PlayerName: "LordCereth", PlayerRank: 20, ... }
                ]
            }],
            MatchId: 12345,
            State: 1,
            PlayMode: 101,
            VsCPU: true,       // <-- Always VS CPU
            StageId: 20001,
            ...
        },
        ds: { ServerId: 6789, State: 1, address: "192.168.0.55", version: "70571" },
        MatchType: 1,
        StageId: 20001
    }
};
```

**Step 3**: Send `NotifyMatchBegin` (304)
```javascript
payload = {
    packetId: decoded.packetId,
    messageType: 304,
    NotifyMatchBegin: { MatchId: 12345 }
};
```

### 2.3 Key Observations

| Aspect | Evidence |
|--------|----------|
| **VsCPU always true** | `VsCPU: true` hardcoded in NotifyMatchMade |
| **Hardcoded player IDs** | 10010, 10011 only |
| **Hardcoded match ID** | 12345 |
| **Hardcoded stage** | 20001 |
| **No real matchmaking** | No queue, no candidate selection, no dedicated server allocation |
| **No matchmaking timeout** | Immediate response with fake data |
| **No re-matching** | messageType 202 (RequestCancelMatching) mapped to NotifyMatchBegin (misuse) |
| **IP whitelist only auth** | No session tokens, no cabinet authentication |

### 2.4 Match Flow (Legacy)

```
Cabinet                              Server
  │                                    │
  │── POST /matching/server ──────────>│  (HTTP, bootstraps TCP)
  │<── { ip_addr: "host:6666" } ──────│
  │                                    │
  │── TCP connect ────────────────────>│  (authorized by IP)
  │── RequestEntryMatching (200) ─────>│
  │<── ResponseEntryMatching (201) ───│  (ack, timeout=45)
  │<── NotifyMatchMade (302) ─────────│  (fake VsCPU match)
  │<── NotifyMatchBegin (304) ────────│  (match_id=12345)
  │                                    │
  │   [Cabinet starts battle]          │
```

---

## 3. Proposed Architecture (PROPOSED)

### 3.1 Components

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  HTTP API   │────>│ Match Queue  │────>│  RoomMgr    │────>│ Battle Sess  │
│ (FastAPI)   │     │   (Redis)    │     │ (PostgreSQL)│     │  (PostgreSQL)│
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
       │                   │                    │                    │
       │              ┌────┴────┐          ┌────┴────┐          ┌───┴───┐
       │              │  Queue  │          │  Room   │          │Battle │
       │              │ Workers │          │  State  │          │ State │
       │              └─────────┘          └─────────┘          └───────┘
       │
  ┌────┴─────┐
  │ TCP/Proto│  (port 6666)
  │  Server  │
  └──────────┘
```

### 3.2 Queue (Redis)

- **Sorted set** `match:queue:{mode}` — players ordered by wait time
- **Hash** `match:player:{id}` — player session data
- **TTL** on queue entries to auto-expire stale requests
- **Lock** `match:lock:{mode}` — prevents duplicate candidate selection

### 3.3 Matchmaker Worker

Async worker that runs every 1-2 seconds:
1. Pop candidates from sorted set
2. Group by compatible criteria (mode, rank range, location)
3. Create match record in PostgreSQL
4. Allocate dedicated server room
5. Notify players via TCP push (NotifyMatchMade)

### 3.4 Room Management (PostgreSQL)

New tables (not in legacy schema):

| Table | Purpose |
|-------|---------|
| `match_sessions` | Active match records with state machine |
| `match_players` | Players in each match |
| `dedicated_servers` | Available battle servers |
| `battle_sessions` | Battle lifecycle tracking |

### 3.5 HTTP Endpoints (Proposed)

| Endpoint | Purpose |
|----------|---------|
| `POST /matching/server` | Bootstrapping (already implemented) |
| `POST /matching/match_id/generate` | Generate unique match ID |
| `POST /matching/cancel` | Player cancels matchmaking |
| `POST /matching/status` | Query match status |
| `POST /matching/room/list` | List available rooms (for burst mode) |

### 3.6 TCP Message Sequence (Proposed)

**Standard Match (1v1)**:
```
Cabinet                           Server
  │                                 │
  │── RequestEntryMatching (200) ──>│
  │<── ResponseEntryMatching (201) ─│  (queued)
  │                                 │  [matchmaker finds opponent]
  │<── NotifyMatchMade (302) ──────│  (real match data)
  │<── NotifyMatchBegin (304) ─────│  (match_id from DB)
  │                                 │
  │── ReadySignal ─────────────────>│
  │<── NotifyMatchReady ───────────│
  │                                 │
  │   [Battle begins]               │
```

**Co-op Burst Mode**:
```
Cabinet                           Server
  │                                 │
  │── RequestEntryBurstGroup (208) >│  (register)
  │<── ResponseEntryBurstGroup (209)│
  │                                 │
  │── RequestChangeBurstGroupMode   │  (create room)
  │<── ResponseChangeBurstGroupMode │
  │                                 │
  │   [Other cabinets join]         │
  │── RequestBurstGroupSelect (216) >│  (join room)
  │<── ResponseBurstGroupSelect (217│
  │<── NotifyBurstGroupApply (308) ─│  (broadcast to room)
  │<── NotifyBurstGroupUpdated (307)│  (broadcast to room)
  │                                 │
  │<── NotifyBurstMade (310) ──────│  (all players ready)
  │<── NotifyBurstMeets (311) ─────│  (battle start)
```

### 3.7 Burst Mode (Co-op) — Legacy vs Proposed

| Aspect | Legacy | Proposed |
|--------|--------|----------|
| Room storage | In-memory array | Redis + PostgreSQL |
| Player lookup | Linear scan | Hash map by PlayerId |
| Concurrency | No locking | Redis distributed lock |
| Room cleanup | Never | TTL-based expiration |
| Max players | Hardcoded 2 | Configurable per stage |
| Reconnection | Not supported | Session resume |

---

## 4. Implementation Notes

### 4.1 Proto Message Anomalies

From forensic audit (`docs/PROTOCOL_MAP.md`):

| messageType | Issue |
|-------------|-------|
| 214 | Mapped to `NotifyMatchBreak RequestUpdateBurstGroup` — type aliasing |
| 206 | Mapped to `NotifyMatchEscape RequestJoinMatching` — type aliasing |
| 202 | Mapped to `NotifyMatchBegin RequestCancelMatching` — confusing reuse |

The legacy code uses these aliases; the Python implementation must preserve them for backward compatibility.

### 4.2 Backward Compatibility Requirements

1. `POST /matching/server` must return `{ "ip_addr": "host:port" }` exactly
2. TCP framing: 4-byte LE length prefix + protobuf payload
3. All existing messageType values must be preserved
4. VsCPU match must still work (single-player fallback)

### 4.3 Security Considerations

- Legacy has no auth beyond IP whitelist
- Proposed: Session tokens via HTTP, validated on TCP connect
- Rate limiting on match entry
- Input validation on all protobuf fields

---

## 5. Open Questions

1. Is there a dedicated server binary, or does the Python server act as both matchmaker and battle host?
2. What is the actual battle flow after NotifyMatchBegin? Does the cabinet switch to a different server?
3. Are there any recorded TCP captures of a real 1v1 match (not VsCPU)?
4. What triggers NotifyMatchFailure (204) in the real game?
5. What is the actual timeout behavior for RequestEntryMatching?
