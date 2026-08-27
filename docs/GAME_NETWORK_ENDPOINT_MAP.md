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

| Port | Protocol | Purpose |
|------|----------|---------|
| 4001 | TCP | Game server (main game ↔ backend) |
| 6666 | TCP | NESYS service (card reader ↔ backend) |
| 4000 | HTTP | WebAPI (config/status) |

## 4. DLL Dependencies for Network

| DLL | Purpose |
|-----|---------|
| `NesysNet.dll` | Network abstraction for NESYS |
| `NesysService.exe` | Card/network service process |
| `ws2_32.dll` | Winsock (standard Windows TCP/UDP) |

## 5. UE4 Content Network Plugins

From `SavedEngine.ini`:
- `NesysClient/Content` — UE4 plugin for NESYS client
- `TestMode/Content` — UE4 plugin for test mode

## 6. Test Mode Network Menu

From `tm_network.json`:
- **Game server connection test** (`game_server_test`)
- **NESYS service connection test** (`nesys_test`)

The game connects to these endpoints on startup and maintains persistent connections for gameplay and card operations.

## 7. Implications for Our Server

Our FastAPI backend must listen on:
- `4001` — Game server TCP endpoint (our `app/tcp_server.py`)
- `6666` — NESYS service (if implementing card operations)
- `4000` — HTTP REST (our FastAPI default port is 8000; may need configuration)
