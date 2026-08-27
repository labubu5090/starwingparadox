# Starwing Port Ownership

## Port Model

| Port | Expected Owner | Role | Protocol | Evidence | Confidence |
|------|---------------|------|----------|----------|------------|
| 4000 | Unknown/WebAPI | Optional UI service or client | HTTP | Game config `WebAPIPort=4000`; NesysService binary has 5 uint16 refs | LOW |
| 4001 | Python HTTP server | Game server (main backend) | HTTP | Game config `GameServerPort=4001`; no NesysService refs | HIGH |
| 6666 | NesysService.exe | NESYS card/network service | TCP/Custom | Game config `NesysServerPort=6666`; NesysService binary has 1 uint16 ref; NESYS plugin in game | HIGH |
| 8000 | Python dev server | Development HTTP server | HTTP | Current implementation; not game-facing | N/A |

## Evidence

### Port 4001 — Game Server
- `test_mode_setting.json`: `GameServerPort: 4001`
- `GameServerIP: 127.0.0.1`
- No reference to 4001 in NesysService.exe
- Python server designed for this port (`app_port: int = 4001` in config.py)
- Game did NOT connect to 4001 in G2 (because NesysService wasn't running?)

### Port 6666 — NESYS Service
- `test_mode_setting.json`: `NesysServerPort: 6666`
- `NesysServerIP: 127.0.0.1`
- NesysService.exe binary contains port 6666 as uint16
- Game has NesysClient UE4 plugin
- NESYS plugin initialized but could not connect (no service)
- NesysService is a WINHTTP client connecting to `cert3.nesys.jp`

### Port 4000 — Unknown
- `test_mode_setting.json`: `WebAPIPort: 4000`
- `WebAPIIP: 127.0.0.1`
- NesysService binary has 5 uint16 refs to 4000 (in code sections)
- Game did NOT connect to 4000 in G2
- Possibly a web API endpoint for UI or configuration
- LOW confidence — may not be needed for initial boot

### Port 8000 — Development
- Current Python server port
- Not referenced in game config
- Used for development/testing only
- Must NOT be the game runtime port

## Collision Risk

| Scenario | Risk |
|----------|------|
| Python on 4001 + NesysService on 6666 | No collision |
| Python on 4001 + Python on 6666 | No collision |
| NesysService on 4001 + Python on 4001 | COLLISION |
| NesysService on 6666 + Python on 6666 | COLLISION |

## Recommendation

1. Python HTTP server → port 4001
2. NesysService.exe → port 6666 (its native port)
3. Do NOT start Python TCP server on 6666
4. Do NOT implement port 4000 unless evidence requires it
