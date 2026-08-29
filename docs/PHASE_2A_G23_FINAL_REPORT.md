# Phase 2A-G23 Final Report: Local NESYS Port 1042 Contract

**Classification:** `SECURITY_BOUNDARY_REACHED`  
**Date:** 2026-08-29  
**Commit:** Pending

## Executive Summary

G23 determined the complete local client contract for localhost:1042 and its relationship to NesysService.exe. The game attempts TCP connections to localhost:1042 for communication with NesysService, which handles certificate validation and external vendor communication.

## Key Findings

### Port 1042 Protocol
- **Transport:** TCP (IPv4, localhost only)
- **Client:** AcrGame-Win64-Shipping.exe (game launcher)
- **Server:** NesysService.exe (cabinet service controller)
- **Connection pattern:** SYN every 500ms, new source port every ~1s, 5 retries per port
- **G23 SYN attempts:** 35 over 17 seconds
- **G22 SYN attempts:** 40 over 23 seconds
- **All RST:** NesysService not running
- **No data exchanged:** Connection refused before any protocol data

### NesysService Protocol
NesysService implements a full command/response protocol:
- **Client commands (LCOMMAND_*):** CLIENT_START, CONNECT_REQUEST, GAME_START, CARD operations, HTTP access, etc.
- **Server commands (SCOMMAND_*):** CERT_ERROR, CERT_INIT_NOTICE, CERT_REGULAR_NOTICE, NW_ERROR, etc.
- **External communication:** WinHttp to proxy.nesys.jp and cert3.nesys.jp
- **Certificate handling:** CertFindCertificateInStore() with MY\\.Default store

### Certificate Boundary
- **Classification:** SECURITY_BOUNDARY_REACHED
- **Certificate store:** MY\\.Default with 'nesys' subject
- **External endpoints:** proxy.nesys.jp, cert3.nesys.jp (HTTPS)
- **Client certificate:** Used for outbound TLS
- **Private server eligibility:** EXCLUDED - production trust dependency

### CertError Analysis
- **4,575 log lines** do NOT represent 4,575 connection attempts
- **35-40 SYN attempts** over 17-23 seconds
- **CertError** is SCOMMAND_CERT_ERROR from NesysService
- **Cause:** Certificate not found in MY\\.Default store or validation failed
- **Game state:** Enters retry loop, eventually gives up

### Named Pipe
- **No evidence** of \\\\.\\pipe\\nesys_games in either binary
- **NesysService uses** file mapping (_filemap) and mutex (_mutex) for IPC
- **Game communicates** via TCP port 1042, not named pipes

## Architecture Decision

**Option D: Original protected trust dependency prevents implementation**

The game requires NesysService for certificate validation. This is a production trust dependency that cannot be replaced without:
1. Bypassing certificate validation (excluded)
2. Forging vendor certificates (excluded)
3. Impersonating external services (excluded)

## Remaining Work

1. Analyze NesysService command protocol in detail (future phase)
2. Determine if local compatibility adapter is possible for non-certificate functions
3. Assess whether certificate store can be populated from operator-owned sources
4. Document complete command protocol for future reference