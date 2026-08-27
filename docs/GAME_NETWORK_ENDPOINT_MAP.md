# Game Network Endpoint Map

## 1. Architecture Overview

Starwing Paradox uses a **dual-process architecture**:
- `AcrGame-Win64-Shipping.exe` — Main game (UE4 shipping binary)
- `NesysService.exe` — NESYS card/network service (runs as separate process)

## 2. Network Configuration Source

From `D DRIVE CONTENTS\Saved\ACRSaved\TestMode\Setting\test_mode_setting.json` (YAML-formatted):

| Setting | Value |
|---------|-------|
| GameServerIP | `127.0.0.1` |
| GameServerPort | `4001` |
| NesysServerIP | `127.0.0.1` |
| NesysServerPort | `6666` |
| WebAPIIP | `127.0.0.1` |
| WebAPIPort | `4000` |
| GameServerRetry | `true` |

## 3. Known Endpoints

| Port | Protocol | Purpose | Status |
|------|----------|---------|--------|
| 80 | HTTP | dev.starwing.jp (hardcoded in binary) | VERIFIED_WORKING |
| 4001 | HTTP | Python game server | VERIFIED_WORKING |
| 6666 | TCP | Matching server (returned by /matching/server) | NOT_STARTED |
| 4000 | HTTP | WebAPI (config/status) | UNUSED |
| — | Named pipe | `\\.\pipe\nesys_games\...` (NESYS IPC) | NOT_RUNNING |

**CORRECTION**: Port 6666 is NOT the NESYS named pipe. NESYS IPC uses Windows named pipes.
Port 6666 is the matching server address returned by the HTTP discovery endpoint.

## 4. DLL Dependencies for Network

| DLL | Purpose |
|-----|---------|
| `NesysClient` (UE4 plugin) | NESYS client-side named pipe connection |
| `NesysService.exe` | NESYS server-side named pipe + external HTTP |
| `ws2_32.dll` | Winsock (standard Windows TCP/UDP) |

## 5. NESYS External Service Endpoints

NesysService.exe connects to these external TAITO servers:

| Host | Protocol | Purpose |
|------|----------|---------|
| cert3.nesys.jp | HTTPS | Certificate verification |
| data.nesys.jp | HTTP | Data downloads |
| nesys.taito.co.jp | HTTP | Alive check |
| proxy.nesys.jp | HTTPS | Proxy |
| fjm170920zero.nesica.net | HTTPS | NESICA card service |

**None of these are reachable from this system** (external TAITO infrastructure).

## 6. UE4 Content Network Plugins

From `SavedEngine.ini`:
- `NesysClient/Content` — UE4 plugin for NESYS client
- `TestMode/Content` — UE4 plugin for test mode

## 7. Test Mode Network Menu

From `tm_network.json`:
- **Game server connection test** (`game_server_test`)
- **NESYS service connection test** (`nesys_test`)

## 8. Current Runtime State

| Component | Status |
|-----------|--------|
| HTTP routing chain | WORKING |
| Matching-server discovery | WORKING |
| NESYS named pipe | NOT_RUNNING (NesysService not started) |
| D: drive | NOT_MOUNTED |
| Matching TCP | NOT_STARTED |
| Battle | NOT_IMPLEMENTED |

## 9. Implications

The game's primary network dependency is NESYS named-pipe IPC, not TCP. The HTTP
matching-server discovery succeeds but the game requires NESYS initialization before
it will proceed beyond the offline error screen.

Without NesysService running and D: drive mounted, the game stays in offline mode permanently.
