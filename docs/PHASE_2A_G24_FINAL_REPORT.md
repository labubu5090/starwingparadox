# Phase 2A-G24 Final Report: Offline Capability and Non-Trust Local Command Classification

**Classification:** `TITLE_SCREEN_REACHED_CERT_ERROR_NON_BLOCKING`  
**Date:** 2026-08-29  
**Commit:** Pending

## Executive Summary

G24 determined that the game reaches the title screen despite the certificate error. The CertError is a background retry loop that does NOT block the boot sequence. The game loads 79% of assets (5972/7553) and displays the title screen with animations.

## Key Findings

### CertError is Non-Blocking
- **4,616 CertError log lines** over 108,502 total lines
- **Retry loop**: Every ~16ms, game calls `RequestNetworkInfo`, gets CertError with status[4]
- **Asset preloading continues concurrently**: 5972/7553 assets loaded (79%)
- **Title screen reached**: `WBP_Title_MainDisplay` and `WBP_InsertStart` animations playing
- **Input enabled**: Title screen waits for player to press Start

### Boot Sequence
1. Launcher starts (T+0s)
2. Shipping starts (T+1s)
3. HTTP timeouts configured (60/60/30s)
4. Error table loaded (13 codes, -1200 to -1212)
5. First CertError (T+4s, line 23016)
6. Asset preloading runs concurrently
7. External HTTPS to 100.60.248.8:443 (T+60s)
8. Title screen reached (T+180s)

### Capability Levels
- **LEVEL_0 (Process Start)**: CURRENTLY_OBSERVED
- **LEVEL_1 (Local Boot)**: CURRENTLY_OBSERVED
- **LEVEL_2 (Local UI)**: CURRENTLY_OBSERVED - Title screen functional
- **LEVEL_3 (Private Server Unauthenticated)**: STATICALLY_REACHABLE
- **LEVEL_4 (Player Session)**: BLOCKED_CERTIFICATE_TRUST
- **LEVEL_5 (Matching)**: BLOCKED_UNKNOWN_FLOW
- **LEVEL_6 (Battle)**: BLOCKED_UNKNOWN_FLOW
- **LEVEL_7 (Result)**: STATICALLY_REACHABLE

### Private Server Implication
The game reaches the title screen without certificate validation. A private server can implement:
- Local status endpoints (LEVEL_3)
- Result persistence (LEVEL_7)
- Basic game flow without production identity

The private server does NOT need to bypass certificate validation to reach the title screen.

### Network Observations
- Port 1042: No SYN attempts (NesysService not running)
- Port 5233: OpenCode health checks continue normally
- External: 100.60.248.8:443 (different IP from G22/G23)
- SSDP discovery: Active (UPnP)

### Error Codes Loaded
- Id[45]: HTTP error (-1200)
- Id[46]: Response wait failed (-1201)
- Id[47]: Response code not 200 (-1202)
- Id[48]: Response header code not 0 (-1203)
- Id[49]: Card lock (-1204)
- Id[50]: Response JSON design failed (-1205)
- Id[51]: Response parameter abnormal (-1206)
- Id[52]: Client version abnormal (-1207)
- Id[53]: Data version abnormal (-1208)
- Id[54]: Player ID abnormal (-1209)
- Id[55]: NESYS card number abnormal (-1210)
- Id[56]: Data base abnormal (-1211)
- Id[57]: Card usage only valid return called (-1212)

## Architecture Decision

The private server can implement local status and result persistence without certificate trust. Player identity, matching, and battle require further protocol investigation.

## Remaining Work

1. Investigate what happens after all 7553 assets finish loading
2. Capture the title screen -> menu transition
3. Determine if card/player flow can be implemented locally
4. Test private server endpoints with live game client
