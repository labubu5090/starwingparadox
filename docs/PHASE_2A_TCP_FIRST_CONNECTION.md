# Phase 2A: TCP First Connection Analysis

## Date: 2026-08-28

## Status: ANALYSIS_COMPLETE

## Correction Note (2026-08-28)

**RENDERING_CRASH_STATUS**: NOT_CONFIRMED_AS_SPONTANEOUS

The operator previously stated that the apparent game crash occurred when the operator forcibly closed the game. The rendering crash (FRCPassPostProcessAA::Process) is NOT confirmed as spontaneous. Do not classify as a current blocker. Do not use operator-forced closure as renderer-failure evidence.

**messageType 103 (0x67)**: CAPTURE_SEQUENCE_CANDIDATE — not proven as PingResponse. Only one capture sequence exists.

**Current primary hypothesis**: First-connection startup timing / server readiness race.

---

## 1. Run Summary

### Run A (TCP-Connected)

- **Time**: 01:21:55 (file close)
- **Duration**: ~28 minutes
- **TCP connections**: 4 attempts, 3 successful
- **TCP server console**: Connections observed
- **Crash**: EXCEPTION_ACCESS_VIOLATION in FRCPassPostProcessAA::Process()

### Run B (HTTP-Only per operator)

- **Time**: 01:42:50 (file close)
- **Duration**: ~3 minutes
- **TCP connections**: 3 attempts (per game log), 0 observed on server console
- **TCP server console**: ZERO connections
- **Crash**: Same rendering crash as Run A

---

## 2. Key Findings

### 2.1 Game-Level TCP Behavior is Identical

Both runs exhibit the exact same game-level TCP sequence:

1. `GameConnect:1` initially
2. HTTP POST matching/server → 200 → `{"ip_addr":"127.0.0.1:6666"}`
3. TCP #1: `SetupConnect` → `Failed to post Ping : Lost Connection` (race condition)
4. `GameConnect` drops to 0, never restores
5. TCP #2+: Successful ping/pong at transport level
6. `bGameConnect` stays 0 despite `WebServer Revived!`
7. SystemDataCheck detects offline → error
8. Crash on SL_Title

### 2.2 First TCP Failure is a Race Condition

The game's TCP client calls `SetupConnect` but sends a Ping before `TryToConnect` completes:

```
SetupConnect / TargetAddress[127.0.0.1:6666]
    ↓ (no TryToConnect)
Failed to post Ping : Lost Connection
```

This is identical in both runs and is a game-level bug.

### 2.3 bGameConnect Never Restores

After the first failure sets `GameConnect:0`, subsequent successful TCP connections never restore it:

```
OnReceivePong / bWebServerLive[1] bNesysServerLive[0] bGameConnect[0] bHttpSuccess[1]
```

The game's state machine only sets `GameConnect:1` during initial connection, not reconnection.

### 2.4 TCP Server Console Discrepancy (Run B)

**CRITICAL**: Run B's game log shows TCP connections with successful ping/pong, but the TCP server console showed zero connections.

Possible explanations:
1. Game connected to a stale TCP server from Run A
2. TCP server was started after game connection attempts
3. Port conflict with multiple TCP server processes

**Status**: UNEXPLAINED

---

## 3. Matching Server Response Verification

### Exact Response

Both runs receive identical HTTP responses:

| Field | Value |
|-------|-------|
| Status code | 200 |
| Content-Type | application/json |
| Body | `{"ip_addr":"127.0.0.1:6666"}` |
| Field name | `ip_addr` |
| Field value | `127.0.0.1:6666` |

### Comparison with Legacy JS

The legacy JS client expects the same format. The response is byte-identical between runs.

---

## 4. Game Caching Investigation

### Observed Cache Behavior

| Cache | Status |
|-------|--------|
| Matching server address | Uses config (.ini) `UseConfigMatchingServer: 1` |
| NESYS state | Not cached (always offline) |
| Session ID | `sessionid[0]` in all pings |
| Previous TCP state | Not cached (fresh connection each time) |
| Game restart count | Unknown |
| Matching initialization flags | `MatchingServerType[None]` throughout |

### Config Source

```
MatchingServer : 127.0.0.1:6666 (UseConfigMatchingServer : 1)
Use Config(.ini)MatchingServer address:127.0.0.1:6666
```

The game uses the config file for the matching server address, not NESYS.

---

## 5. Process State Comparison

### Run A Processes

| Process | Status |
|---------|--------|
| AcrGame.exe | Running (crashed at end) |
| AcrGame-Win64-Shipping.exe | Running (crashed at end) |
| NesysService.exe | NOT RUNNING |
| Python HTTP server | Running on :4001 |
| HTTP proxy | Running on :80 |
| Python TCP server | Running on :6666 |

### Run B Processes

| Process | Status |
|---------|--------|
| AcrGame.exe | Running (crashed at end) |
| AcrGame-Win64-Shipping.exe | Running (crashed at end) |
| NesysService.exe | NOT RUNNING |
| Python HTTP server | Running on :4001 |
| HTTP proxy | Running on :80 |
| Python TCP server | Running on :6666 (per operator) |

### Process Differences

No significant process differences between runs. Both had the same server stack running.

---

## 6. Protocol Evidence

### 0x66 Ping

- Captured in both runs
- 17 bytes sent by game
- Contains packetId and Ping.unixTimestamp
- Server echoes back identical frame

### 0x67 PingResponse

- Captured in TCP server log (Run A)
- Sent by game in response to 0x66
- Same packetId as the 0x66 it responds to
- Classification: CAPTURE_SEQUENCE_CANDIDATE

### messageType 103 Audit

See: `docs/MESSAGE_TYPE_103_AUDIT.md`

---

## 7. Runtime Result

| Metric | Value |
|--------|-------|
| TCP_CONNECTION_STATE | DEPENDS_ON_GAME_FLOW |
| MESSAGE_103_CLASSIFICATION | CAPTURE_SEQUENCE_CANDIDATE |
| MATCHING_RESPONSE_DIFFERENCE | NONE_FOUND |
| STALE_SESSION_DIFFERENCE | POSSIBLE |
| SERVER_START_ORDER_DIFFERENCE | POSSIBLE |
| PRIMARY_BLOCKER | NESYS_OFFLINE → bGameConnect_never_restores |
| RENDERING_CRASH | NOT_CONFIRMED_AS_SPONTANEOUS |

---

## 8. What Was NOT Proven

1. **Ping handshake not confirmed** — Run B never observed on TCP server console
2. **messageType 103 not proven** — Only one capture sequence
3. **Matching battle not tested** — Matching remains NOT_IMPLEMENTED
4. **Real playability not proven** — Game crashes before gameplay
5. **NESYS remains offline** — Primary blocker for game progression

---

## 9. Documentation Updated

- `PROGRESS.md` — Phase 2A status updated
- `docs/TCP_RUNTIME_DIFFERENTIAL_ANALYSIS.md` — Run A vs Run B comparison
- `docs/MESSAGE_TYPE_103_AUDIT.md` — messageType 103 classification
- `docs/STARWING_BOOT_DEPENDENCY_GRAPH.md` — TCP connection state added
