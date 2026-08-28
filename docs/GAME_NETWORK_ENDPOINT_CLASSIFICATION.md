# GAME_NETWORK_ENDPOINT_CLASSIFICATION

## Status

**Classification:** MULTIPLE_CLIENT_PATHS_IDENTIFIED

## Network Paths

### 1. HTTP / HTTPS (WININET, in the Shipping executable)
Primary operator-visible HTTP interface. Endpoints:
- `BindHttpMatchingServer`
- `BindHttpMatchingMatchIdGenerate`
- `BindHttpGameDataSaveData`
- `BindHttpFestResult`
- `BindHttpErrorCallback`
Fixed URLs: `https://log.starwing.jp/acr/public/` (production log), `dev.starwing.jp/mock`.
Role in private server: **DIRECT_SERVER_PROTOCOL** (HIGH confidence).

### 2. Raw TCP sockets (WS2_32)
Battle + matching coordination. Commands incl. `EntryMatching`, `CancelMatching`,
`EntryBurst`, `BurstUpdate`, etc.
Role in private server: **DIRECT_SERVER_PROTOCOL** (HIGH confidence).

### 3. Local named pipe (`\\.\pipe\nesys_games`)
NESYS card operations. Role: **LOCAL_ADAPTER_REQUIRED** (MEDIUM confidence).

### 4. GALAXYIO HTTP (WinHTTP)
Card certificate validation (`https://cert2.nesys.jp`) + AMIC card endpoint.
Role: **PRODUCTION_TRUST_DEPENDENCY** (HIGH) — NOT reproduced by the private server.

## Feature → Path

| Feature | Path |
|---------|------|
| Game startup | HTTP |
| Player card session | Local pipe |
| Matching | TCP + HTTP |
| Battle coordination | TCP |
| Result submission | HTTP |
| Error handling | HTTP + local pipe |

## Private Server Surface (current, NOT game-confirmed)

- HTTP :4001, proxy :80, TCP :6666 — none confirmed as the game's actual targets.
- The game's hardcoded URL uses default HTTP port 80; hosts-file/DNS redirect is operator-action only.

## Endpoint Override

**NO_SUPPORTED_ENDPOINT_OVERRIDE_FOUND.** No game-side config (command line, INI, UE4 config,
env var, registry, XML/JSON) redirects the game to a private-server endpoint. The only
practical redirect is operator-level hosts-file/DNS override — out of scope for G19.

## References

- `artifacts/phase_2a_g19/network_endpoint_classification.json`
- `artifacts/phase_2a_g19/game_command_dispatch.json`
