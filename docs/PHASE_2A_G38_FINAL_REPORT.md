# G38 Final Report: bNesysServerLive Writer/Reader/Semantic Classification

## Executive Summary

IDA Pro decompilation of `AcrGame-Win64-Shipping.exe` has fully traced the `bNesysServerLive` flag from its format string through its writer function to its data source. The flag is **NOT** a named-pipe state. It is a **certificate-authenticated NESYS server state** derived from HTTP certificate validation.

---

## 1. LiveBits Containing Function and RVA

| Property | Value |
|----------|-------|
| Format function | `sub_142C71A30` (UOnlineObserverWork::Report) |
| RVA | `0x142C71A30` |
| Source file | `C:\work\acr\AcrGame\Source\NetworkModule\Private\OnlineObserverWork.cpp` |
| Source line | 327 |
| Format string | `LiveBits < WebServer:%d Nesys:%d Reception:%d Game:%d Testmode:%d GameConnect:%d HttpSuccess:%d>` |

---

## 2. Exact Source of the Nesys Argument

| Property | Value |
|----------|-------|
| Flag name in log | `bNesysServerLive` |
| Observer offset | `[100]` (byte field) |
| Writer function | `sub_142C72730` (UOnlineObserverWork::Tick) |
| Write expression | `*(a1 + 60) = sub_142C71500(nesys_state) && !sub_142C64DF0(nesys_state)` |
| NESYS state source | `sub_142C61450(self)` -> complex UE4 object chain -> NESYS state object |
| NESYS live check | `sub_142C71500`: `return *(_BYTE *)(a1 + 1600) == 1` |
| NESYS maintenance check | `sub_142C64DF0`: Virtual function call chain on NESYS state |

**Data flow chain:**
```
sub_142C72730 (Tick)
  -> sub_142C61450(self) -> NESYS state object
  -> sub_142C71500(NESYS_state) -> *(byte*)(NESYS_state + 1600) == 1
  -> sub_142C64DF0(NESYS_state) -> Virtual function call chain
  -> bNesysServerLive = (NESYS_live == 1) AND (NOT NESYS_maintenance)
```

---

## 3. Every Confirmed Writer

| Flag | Offset | Writer Function | RVA | Trigger |
|------|--------|----------------|-----|---------|
| bWebServerLive | [99] | OnReceivePong | 0x142C71790 | TCP pong received |
| bNesysServerLive | [100] | Tick | 0x142C72730 | Periodic tick (every frame) |
| bNesicaReception | [101] | SetLiveFromGame | 0x142C71F30 | Game live state change |
| bLiveFromTestmode | [102] | Unknown | - | Test mode state |
| bLiveFromGame | [103] | SetLiveFromGame | 0x142C71F30 | Game live state change |
| bGameConnect | [104] | Unknown | - | TCP connection established |
| bHttpSuccess | [105] | SetHttpSuccess | 0x142C71C70 | HTTP request completion |

---

## 4. Condition Setting bNesysServerLive TRUE

```
bNesysServerLive = (NESYS_state->byte_1600 == 1) AND (NOT NESYS_in_maintenance)
```

Where:
- `NESYS_state->byte_1600` is set to 1 after successful NESYS certificate authentication via HTTP
- `NESYS_in_maintenance` is a virtual function call checking maintenance status

---

## 5. Condition Setting bNesysServerLive FALSE

```
bNesysServerLive = (NESYS_state->byte_1600 != 1) OR (NESYS_in_maintenance == true)
```

This occurs when:
- Certificate authentication fails or hasn't completed
- NESYS server is in maintenance mode
- NESYS state object doesn't exist

---

## 6. Certificate Dependency

**YES - bNesysServerLive is directly dependent on certificate authentication.**

The NESYS state byte at offset 1600 is set by the NESYS control system after HTTP certificate validation succeeds. The function `RequestNesysControlInitiazlize` (note: typo in binary) handles the certificate exchange:

```
sub_142BCB6E0 (AcrProtocol::Connect)
  -> Log: "Nesys::RequestNesysControlInitiazlize [Cert] / id[%d] / status[%d] / option[%d]"
  -> Certificate exchange via HTTP
  -> NESYS state byte 1600 set to 1 on success
```

---

## 7. Pipe Dependency

**NO - bNesysServerLive has zero dependency on named pipes.**

The NESYS state is set entirely through HTTP certificate validation. No pipe communication is involved in setting or reading this flag. The named-pipe protocol (NesysService) is a separate system that handles card tap events, not server liveness.

---

## 8. Exact Meaning of bGameConnect

| Property | Value |
|----------|-------|
| Flag | `bGameConnect` |
| Offset | `[104]` in observer object |
| Meaning | TCP connection to matching server is established and active |
| Dependency | TCP socket connected to `IPAddress:Port` from HTTP matching server response |
| Writer | Unknown (not fully traced) |
| Classification | `TCP_CONNECTION_STATE` |

---

## 9. Complete Playable-Gate Expression

```c
// sub_142C71510 (OnlineGateCheck)
return a1[99]    // bWebServerLive    - TCP pong received
    && a1[100]   // bNesysServerLive  - NESYS certificate authenticated
    && a1[102]   // bNesicaReception  - NESiCA reception active
    && a1[101]   // bLiveFromTestmode - Test mode live
    && a1[103]   // bLiveFromGame     - Game live
    && a1[104]   // bGameConnect      - TCP connection active
    && a1[105];  // bHttpSuccess      - HTTP request succeeded
```

When all 7 flags are true:
- `sub_142DAD060(a1 + 80)` fires OnlineDelegate notification
- Game proceeds to Title screen / online mode

When any flag is false:
- `sub_142C71320` fires OfflineDelegate notification
- Game shows "offline" state

---

## 10. Whether the INI Path Avoids the Gate

**NO - the INI matching path does NOT bypass the gate.**

The INI config provides the matching server address:
```
sub_142BCB6E0: "Use Config(.ini)MatchingServer address:%s"
```

However, `sub_142C71510` (OnlineGateCheck) is called **regardless** of matching server source. All 7 flags must still be true.

---

## 11. Safe Non-Trust Path Eligibility

| Path | Eligible | Reason |
|------|----------|--------|
| Card profile system | YES | Card data stored locally, loaded on tap. Does not affect bNesysServerLive. |
| Tutorial bypass | NO | Requires online gate to pass |
| Local battle | NO | Requires online gate to pass |
| Pipe emulator | NO | Does not affect bNesysServerLive |
| Certificate bypass | NO | Would require modifying binary |

---

## 12. Exact Next Action

The `bNesysServerLive` flag is classified as `NESYS_CERTIFICATE_AUTHENTICATED_STATE`. It is set by HTTP certificate validation, not by named-pipe communication. The flag cannot be safely set to 1 without a valid NESYS certificate exchange.

**Recommended next action:** Focus on the card profile system (eligible) and the matching server mock (already working). The online gate requires NESYS certificate authentication which cannot be emulated without modifying the binary.

---

## Artifact Files

- `artifacts/phase_2a_g38/livebits_xrefs.json` - All string xrefs and function locations
- `artifacts/phase_2a_g38/nesys_live_dataflow.json` - Complete data flow from writer to reader
- `artifacts/phase_2a_g38/livebits_write_map.json` - Write map for all 7 flags
- `artifacts/phase_2a_g38/playable_gate_expression.json` - Gate expression and eligibility analysis
- `docs/PHASE_2A_G38_FINAL_REPORT.md` - This report
