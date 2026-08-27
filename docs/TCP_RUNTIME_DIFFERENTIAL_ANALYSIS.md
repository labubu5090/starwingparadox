# TCP Runtime Differential Analysis: Run A vs Run B

## Date: 2026-08-28

## Correction Note (2026-08-28)

**RENDERING_CRASH_STATUS**: NOT_CONFIRMED_AS_SPONTANEOUS

The operator previously stated that the apparent game crash occurred when the operator forcibly closed the game. The rendering crash (FRCPassPostProcessAA::Process) is NOT confirmed as spontaneous. Do not classify as a current blocker. Do not use operator-forced closure as renderer-failure evidence.

**messageType 103 (0x67)**: CAPTURE_SEQUENCE_CANDIDATE — not proven as PingResponse. Only one capture sequence exists.

**Current primary hypothesis**: First-connection startup timing / server readiness race.

## Executive Summary

Run A (01:21) and Run B (01:41) exhibited **identical game-level TCP behavior**. Both runs:
- Failed the first TCP attempt with `"Failed to post Ping : Lost Connection"`
- Successfully connected on subsequent attempts (per game log)
- Never set `bGameConnect` to 1 after the initial failure
- Remained NESYS offline throughout
- Crashed with the same rendering bug (`FRCPassPostProcessAA::Process()`)

**The critical discrepancy**: Run B's TCP server console showed zero connections, but the game log shows TCP connections. This is unexplained.

---

## 1. Timeline Comparison

### Run A (TCP-Connected)

| Time (game log) | Event | Line |
|-----------------|-------|------|
| 16:51:05 | GameModeBoot BeginPlay | 593 |
| 16:51:05 | CertError spam begins | 23020 |
| 16:53:16 | GameConnect:1 | 108231 |
| 16:53:16 | HTTP POST matching/server (1st) | 108250 |
| 16:53:18 | HTTP 200, IPAddress[127.0.0.1:6666] | 108475 |
| 16:53:18 | TCP #1: SetupConnect | 108530 |
| 16:53:18 | TCP #1: **FAILED** - Failed to post Ping | 108531 |
| 16:53:18 | SystemDataCheck: IsOnline[0], offline error | 108667-108679 |
| 16:54:18 | TCP #2: **SUCCESS** | 109041 |
| 16:54:18 | Ping/Pong OK, bGameConnect[0] | 109045-109047 |
| 16:54:33 | TCP #2: Disconnect | 109179 |
| 16:54:50 | TCP #3: **SUCCESS** | 109829 |
| 16:55:03 | TCP #4: **SUCCESS**, heartbeat continues | 110171 |
| 17:21:55 | **CRASH** on SL_Title | 112079 |
| 01:21:55 | Log file closed | 112115 |

**Duration**: ~28 minutes. **TCP connections on server console**: YES.

### Run B (HTTP-Only per operator)

| Time (game log) | Event | Line |
|-----------------|-------|------|
| 17:39:xx | GameModeBoot BeginPlay | - |
| 17:39:xx | CertError spam begins | - |
| 17:41:44 | GameConnect:1 | 107730 |
| 17:41:44 | HTTP POST matching/server (1st) | 107749 |
| 17:41:45 | HTTP 200, IPAddress[127.0.0.1:6666] | 107974 |
| 17:41:45 | TCP #1: SetupConnect | 108029 |
| 17:41:45 | TCP #1: **FAILED** - Failed to post Ping | 108030 |
| 17:41:45 | GameConnect drops to 0 | 108520 |
| 17:42:08 | TCP #2: **SUCCESS** (per game log) | 108790 |
| 17:42:08 | Ping/Pong OK, bGameConnect[0] | 108794-108796 |
| 17:42:25 | TCP #3: **SUCCESS** (per game log) | 109136 |
| 17:42:50 | **CRASH** on SL_Title | 109189 |
| 01:42:50 | Log file closed | 109225 |

**Duration**: ~3 minutes. **TCP connections on server console**: NO (zero observed).

---

## 2. Identical Behaviors

### 2.1 First TCP Failure (Race Condition)

Both runs exhibit the **exact same race condition** on the first TCP attempt:

```
SetupConnect / TargetAddress[127.0.0.1:6666]
    ↓ (no TryToConnect)
Failed to post Ping : Lost Connection
```

The game's TCP client calls `SetupConnect` but attempts to send a Ping before `TryToConnect` completes the TCP handshake. This is a game-level bug in the TCP initialization sequence.

**Evidence**:
- Run A: line 108530 → 108531
- Run B: line 108029 → 108030

### 2.2 bGameConnect Never Restores to 1

After the first TCP failure sets `GameConnect:0`, subsequent successful TCP connections never restore it:

```
OnReceivePong / bWebServerLive[1] bNesysServerLive[0] bGameConnect[0] bHttpSuccess[1]
```

The `WebServer Revived!` event fires, but `bGameConnect` remains 0. The game's state machine only sets `GameConnect:1` during the initial connection, not during reconnection.

**Evidence**:
- Run A: lines 109047, 109835, 110179
- Run B: lines 108796, 109142

### 2.3 NESYS Always Offline

Both runs show:
- `Nesys:0` throughout
- `bNesysServerLive[0]`
- `CertError` spam during boot
- `IsOnline[0]` in SystemDataCheck
- "現在オフラインの為チェック出来ません" (offline error)

### 2.4 Same Rendering Crash

Both runs crash with the identical stack trace:
```
EXCEPTION_ACCESS_VIOLATION reading address 0x00000000
FRCPassPostProcessAA::Process() at postprocessaa.cpp:289
```

This is a null pointer dereference in the rendering thread's post-processing anti-aliasing pass. Not related to networking.

### 2.5 Matching Server Response Identical

Both runs receive the same HTTP response:
- Status: 200
- Body: `{"ip_addr":"127.0.0.1:6666"}`
- Change: 1 (first request), 0 (subsequent)

---

## 3. Critical Discrepancy: TCP Server Console

### Observation

| Metric | Run A | Run B |
|--------|-------|-------|
| TCP server console connections | YES | ZERO |
| Game log TCP connections | YES | YES |
| bGameConnect after pong | 0 | 0 |

### Possible Explanations

1. **Stale TCP server**: Run A's TCP server was still running when Run B started. The game connected to the old server instance, not the new one the user was monitoring.

2. **Server startup timing**: The TCP server was started after the game's connection attempts. The game connected to a socket that was briefly available during server restart.

3. **Port conflict**: Multiple TCP server processes were bound to port 6666. The game connected to a different process than the one being monitored.

4. **Game log staleness**: The game log entries for Run B's TCP connections are from a cached/deferred operation, not actual real-time connections.

### Status: UNEXPLAINED

This discrepancy requires further investigation. The game log evidence is strong (successful ping/pong exchange with decoded PingId), but the server-side observation contradicts it.

---

## 4. Game-Level TCP Flow Analysis

### Connection Sequence

```
1. GameConnect:1 (initial state)
2. HTTP POST matching/server → 200 {"ip_addr":"127.0.0.1:6666"}
3. SetConnectAddress / 127.0.0.1:6666
4. "Error No MatchingServer so initialize Nesys before."
5. TcpThread::Connect / Start Connect
6. TcpThread::SetupConnect / TargetAddress[127.0.0.1:6666]
7. [FIRST ATTEMPT FAILS HERE - race condition]
8. GameConnect drops to 0
9. [SUBSEQUENT ATTEMPTS succeed at transport level]
10. Ping/Pong exchange works
11. bGameConnect stays 0
12. SystemDataCheck detects offline → error
13. Game loops between Title and SystemDataCheck
14. Eventually crashes (rendering bug)
```

### Protocol Observed

- **Ping (0x66)**: 17 bytes sent by game
- **Pong response**: Received and decoded as `OnDecode_Ping: PingId:N`
- ** messageType 0x67**: Not observed in either run's game log (game never sent it after the TCP server echo fix)

---

## 5. Runtime State Classification

| State | Classification |
|-------|---------------|
| HTTP_CONNECTION | CONFIRMED |
| MATCHING_SERVER_DISCOVERY | CONFIRMED |
| MATCHING_SERVER_RESPONSE | CONFIRMED (identical both runs) |
| TCP_LISTENER | RUNNING |
| TCP_CONNECTION_ATTEMPT | GAME_LOG_SHOWS_ATTEMPTS |
| TCP_CONNECTION_SUCCESS | GAME_LOG_SHOWS_SUCCESS (unverified on server) |
| TCP_CONNECTION_OBSERVED_ON_SERVER | Run A: YES, Run B: NO |
| TCP_DISCONNECT | Run A: YES, Run B: YES (per game log) |
| NESYS_STATUS | OFFLINE |
| CARD_PLAY | BLOCKED |
| PRIMARY_TCP_BLOCKER | bGameConnect_never_restores_after_first_failure |
| RENDERING_CRASH | NOT_CONFIRMED_AS_SPONTANEOUS |
| GAME_LEVEL_BEHAVIOR | IDENTICAL_BETWEEN_RUNS |

---

## 6. Conclusions

1. **The game's TCP behavior is identical in both runs.** The difference is not in the game code or protocol handling, but in the server-side observation.

2. **The first TCP failure is a game-level race condition.** The game sends a Ping before the TCP handshake completes. This sets `GameConnect:0` permanently.

3. **bGameConnect never restores.** Even after successful TCP connections and pong exchanges, the game-level connection state stays at 0. This prevents the game from progressing past the offline error.

4. **The TCP server console discrepancy in Run B is unexplained.** The game log shows TCP connections with successful ping/pong, but the server console showed zero connections. This needs investigation.

5. **The rendering crash is unrelated to networking.** Both runs crash with the same null pointer dereference in the post-processing anti-aliasing pass.

6. **NESYS remains the primary blocker.** Without NesysService running, the game stays in offline mode, `bGameConnect` never restores, and gameplay is impossible.

---

## 7. Required Next Steps

1. Investigate why Run B's TCP server console showed zero connections despite game log showing TCP connections
2. Verify which TCP server process the game connected to during Run B
3. Check for stale TCP server processes from Run A
4. Do NOT add more TCP message handlers until the connection discrepancy is resolved
5. Do NOT fabricate NESYS online status
6. Focus on NESYS initialization failure (the root cause of offline mode)
