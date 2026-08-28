# NESYS Protocol Confidence Matrix

**Date**: 2026-08-28
**Phase**: 2A-G16
**Workstream**: E

## Overview

This matrix documents the protocol confidence level for all identified LCOMMAND and SCOMMAND values based on G13 evidence. Field meanings, payload values, and authentication material are NOT invented.

## LCOMMAND Values (Game → Service)

### Confirmed Commands

| Symbolic Name | ID | Direction | Min Frame Size | Known Fields | Unknown Fields | Ordering | Counterpart | Confidence | Source RVA | Clean-room Eligible | Implementation Status |
|---------------|-----|-----------|----------------|--------------|----------------|----------|-------------|------------|------------|--------------------|-----------------------|
| LCOMMAND_CLIENT_START | -- | Game→Service | 0 (empty) | None | All | First | SCOMMAND_CLIENT_START_REPLY | HIGH | G13 analysis | YES | NOT_IMPLEMENTED |
| LCOMMAND_CLIENT_END | -- | Game→Service | 0 (empty) | None | All | Last | None | HIGH | G13 analysis | YES | NOT_IMPLEMENTED |
| LCOMMAND_PING | 0x66 | Game→Service | 0 (empty) | None | All | Any | SCOMMAND_PING_RESPONSE | HIGH | G13 analysis | YES | IMPLEMENTED (handler exists) |

### Protocol-Identified Commands (from G13 pipe protocol analysis)

| Symbolic Name | Direction | Min Frame Size | Known Fields | Unknown Fields | Ordering | Counterpart | Confidence | Source | Clean-room Eligible | Implementation Status |
|---------------|-----------|----------------|--------------|----------------|----------|-------------|------------|--------|--------------------|-----------------------|
| LCOMMAND_CARD_READ | Game→Service | UNKNOWN | Card operation structure | All fields | Any | SCOMMAND_CARD_DATA | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| LCOMMAND_CARD_WRITE | Game→Service | UNKNOWN | Card operation structure | All fields | Any | SCOMMAND_CARD_RESULT | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| LCOMMAND_CARD_CHECK | Game→Service | UNKNOWN | Card operation structure | All fields | Any | SCOMMAND_CARD_STATUS | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| LCOMMAND_NEWS_REQUEST | Game→Service | UNKNOWN | None observed | All | Any | SCOMMAND_NEWS_DATA | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| LCOMMAND_EVENT_REQUEST | Game→Service | UNKNOWN | None observed | All | Any | SCOMMAND_EVENT_DATA | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| LCOMMAND_LOG_UPLOAD | Game→Service | UNKNOWN | None observed | All | Any | SCOMMAND_LOG_RESULT | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| LCOMMAND_MATCH_REQUEST | Game→Service | UNKNOWN | None observed | All | Any | SCOMMAND_MATCH_RESPONSE | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| LCOMMAND_MATCH_CANCEL | Game→Service | UNKNOWN | None observed | All | Any | SCOMMAND_MATCH_CANCEL_ACK | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| LCOMMAND_BURST_GROUP_JOIN | Game→Service | UNKNOWN | None observed | All | Any | SCOMMAND_BURST_GROUP_JOIN_ACK | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| LCOMMAND_BURST_GROUP_LEAVE | Game→Service | UNKNOWN | None observed | All | Any | SCOMMAND_BURST_GROUP_LEAVE_ACK | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |

### Unknown LCOMMAND Values

The G13 analysis identified 47 total LCOMMAND types. The following remain unspecified:

| Count | Status | Confidence | Source |
|-------|--------|------------|--------|
| 37 | UNKNOWN | LOW | G13 count only |

## SCOMMAND Values (Service → Game)

### Confirmed Commands

| Symbolic Name | ID | Direction | Min Frame Size | Known Fields | Unknown Fields | Ordering | Counterpart | Confidence | Source RVA | Clean-room Eligible | Implementation Status |
|---------------|-----|-----------|----------------|--------------|----------------|----------|-------------|------------|------------|--------------------|-----------------------|
| SCOMMAND_CLIENT_START_REPLY | -- | Service→Game | 0 (empty) | None | All | After LCOMMAND_CLIENT_START | LCOMMAND_CLIENT_START | HIGH | G13 analysis | YES | NOT_IMPLEMENTED |
| SCOMMAND_PING_RESPONSE | 0x67 | Service→Game | 0 (empty) | None | All | After LCOMMAND_PING | LCOMMAND_PING | HIGH | G13 analysis | YES | IMPLEMENTED (handler exists) |
| SCOMMAND_CERT_ERROR | -- | Service→Game | UNKNOWN | None observed | All | After certificate failure | None | HIGH | G13 analysis | YES | NOT_IMPLEMENTED |
| SCOMMAND_NW_ERROR | -- | Service→Game | UNKNOWN | None observed | All | After network failure | None | HIGH | G13 analysis | YES | NOT_IMPLEMENTED |
| SCOMMAND_NWRECOVER_NOTICE | -- | Service→Game | UNKNOWN | None observed | All | After network recovery | None | HIGH | G13 analysis | YES | NOT_IMPLEMENTED |

### Protocol-Identified Commands (from G13 pipe protocol analysis)

| Symbolic Name | Direction | Min Frame Size | Known Fields | Unknown Fields | Ordering | Counterpart | Confidence | Source | Clean-room Eligible | Implementation Status |
|---------------|-----------|----------------|--------------|----------------|----------|-------------|------------|--------|--------------------|-----------------------|
| SCOMMAND_CARD_DATA | Service→Game | UNKNOWN | Card operation structure | All fields | After LCOMMAND_CARD_READ | LCOMMAND_CARD_READ | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| SCOMMAND_CARD_RESULT | Service→Game | UNKNOWN | Card operation structure | All fields | After LCOMMAND_CARD_WRITE | LCOMMAND_CARD_WRITE | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| SCOMMAND_CARD_STATUS | Service→Game | UNKNOWN | Card operation structure | All fields | After LCOMMAND_CARD_CHECK | LCOMMAND_CARD_CHECK | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| SCOMMAND_NEWS_DATA | Service→Game | UNKNOWN | None observed | All | After LCOMMAND_NEWS_REQUEST | LCOMMAND_NEWS_REQUEST | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| SCOMMAND_EVENT_DATA | Service→Game | UNKNOWN | None observed | All | After LCOMMAND_EVENT_REQUEST | LCOMMAND_EVENT_REQUEST | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| SCOMMAND_LOG_RESULT | Service→Game | UNKNOWN | None observed | All | After LCOMMAND_LOG_UPLOAD | LCOMMAND_LOG_UPLOAD | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| SCOMMAND_MATCH_RESPONSE | Service→Game | UNKNOWN | None observed | All | After LCOMMAND_MATCH_REQUEST | LCOMMAND_MATCH_REQUEST | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| SCOMMAND_MATCH_CANCEL_ACK | Service→Game | UNKNOWN | None observed | All | After LCOMMAND_MATCH_CANCEL | LCOMMAND_MATCH_CANCEL | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| SCOMMAND_BURST_GROUP_JOIN_ACK | Service→Game | UNKNOWN | None observed | All | After LCOMMAND_BURST_GROUP_JOIN | LCOMMAND_BURST_GROUP_JOIN | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |
| SCOMMAND_BURST_GROUP_LEAVE_ACK | Service→Game | UNKNOWN | None observed | All | After LCOMMAND_BURST_GROUP_LEAVE | LCOMMAND_BURST_GROUP_LEAVE | MEDIUM | G13 analysis | YES | NOT_IMPLEMENTED |

### Unknown SCOMMAND Values

The G13 analysis identified 44 total SCOMMAND types. The following remain unspecified:

| Count | Status | Confidence | Source |
|-------|--------|------------|--------|
| 34 | UNKNOWN | LOW | G13 count only |

## Protocol Summary

| Metric | Value | Confidence | Source |
|--------|-------|------------|--------|
| Total LCOMMAND types | 47 | MEDIUM | G13 analysis |
| Total SCOMMAND types | 44 | MEDIUM | G13 analysis |
| Confirmed LCOMMAND | 3 | HIGH | G13 analysis |
| Confirmed SCOMMAND | 5 | HIGH | G13 analysis |
| Protocol-identified LCOMMAND | 10 | MEDIUM | G13 analysis |
| Protocol-identified SCOMMAND | 10 | MEDIUM | G13 analysis |
| Unknown LCOMMAND | 34 | LOW | G13 count only |
| Unknown SCOMMAND | 29 | LOW | G13 count only |

## Evidence Limitations

1. **Field meanings not evidenced**: No payload structure analysis possible from static binary
2. **Payload formats not evidenced**: No runtime captures exist
3. **Checksum algorithms not evidenced**: No protocol analysis possible
4. **Session identifiers not evidenced**: Cannot determine connection multiplexing
5. **Card data formats not evidenced**: Cannot determine card operation semantics
6. **Authentication material not evidenced**: Cannot determine security protocol
7. **Timing relationships not evidenced**: Cannot determine command ordering
8. **Error codes not evidenced**: Cannot determine failure semantics

## Clean-room Test Eligibility

| Command | Eligible | Rationale |
|---------|----------|-----------|
| LCOMMAND_CLIENT_START | YES | Observable lifecycle event |
| LCOMMAND_CLIENT_END | YES | Observable lifecycle event |
| LCOMMAND_PING | YES | Observable command ID |
| SCOMMAND_CLIENT_START_REPLY | YES | Observable lifecycle event |
| SCOMMAND_PING_RESPONSE | YES | Observable command ID |
| SCOMMAND_CERT_ERROR | YES | Observable error behavior |
| SCOMMAND_NW_ERROR | YES | Observable error behavior |
| SCOMMAND_NWRECOVER_NOTICE | YES | Observable recovery behavior |
| All other commands | YES | Observable command IDs (field meanings unknown) |

---

## G19 Audit Note (Game-Client Evidence Update)

**Date**: 2026-08-29
**Phase**: 2A-G19
**Classification**: GAME_CLIENT_CONTRACT_SUFFICIENT_FOR_NEXT_IMPLEMENTATION

G19 re-audited the protocol identification basis using the game client's own binaries. The
G13-derived NESYS confidence values above are based on inferred pipe protocol analysis. G19
static analysis adds the following, and adjusts certain confidence evaluations:

### New Game-Side Evidence

1. **Pipe role UNRESOLVED**: The game imports both `ConnectNamedPipe` (server-side) and
   `WaitNamedPipeA`/`PeekNamedPipe` (client-side) functions, along with `\\.\pipe\nesys_games`.
   The direction of all NESYS pipe commands (LCOMMAND/SCOMMAND) is therefore **not confirmed**.
   This does NOT change the symbolic names, but the direction and pipe-role assumptions must be
   treated as provisional.

2. **GALAXYIO is HTTP, not pipe**: GALAXYIO.dll uses WinHTTP (`https://cert2.nesys.jp` + AMIC
   card endpoint) and WINUSB, NOT the named pipe. The NESYS card-trust/HTTP path is separate
   from the pipe IPC channel.

3. **CERT_ERROR / NW_ERROR / NWRECOVER_NOTICE**: Their payloads remain **OPAQUE**. No automatic
   FAILED/recovery lifecycle transition may be triggered from G19 evidence. Confidence for
   their *semantics* stays MEDIUM (not HIGH), as it is name-evidence only; the values remain
   clean-room eligible but not behavior-confirmed.

4. **91-command registry reconciliation**: The preserved split is 8 confirmed/high +
   20 protocol-identified/medium + 63 unknown = 91. G19 string analysis enumerated 29
   game-visible command names (HTTP Bind*/Test*, TCP `[Client->Gameserver]*`/`[Dedicated->GameServer]*`,
   NESYS Request*/Callback*) as name-level identification within the 20 protocol-identified tier;
   none promoted to confirmed, none downgraded, none discarded.

### Confidence Adjustments

| Item | Prior (G13) | G19 evaluation |
|------|-------------|----------------|
| NESYS pipe command directions | inferred | UNRESOLVED (pipe role unknown) |
| CERT/NW/NWRECOVER semantics | HIGH (names) | MEDIUM (name only; opaque payload) |
| GALAXYIO | treated as pipe-adjacent | HTTP + USB, separate transport |

All direction, framing, and payload confidence values that rely on the pipe-role assumption
should be re-verified before implementing any live pipe transport (no live pipe in G19).

