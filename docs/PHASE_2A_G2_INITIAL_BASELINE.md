# Phase 2A-G2 Initial Baseline

## Git State

| Item | Value |
|------|-------|
| HEAD | `8465b98` |
| Branch | master |
| Working tree | Clean (untracked: `data/`, `docs/generated/game_content_stats.json`) |

## Game File Hashes (Current)

| File | SHA-256 | Size |
|------|---------|------|
| `AcrGame.exe` | `97800621bb91a2706fbc68ad937679c874b17ac1b2389bddf472be9350e62d6c` | 161,280 |
| `AcrGame-Win64-Shipping.exe` | `ce4c89054bf7c4d833ee8af455a485ac401eead12a80ffc077663a768fd47dc4` | 163,119,104 |
| `NesysService.exe` | `3a968f29b12050dd1b3ae7a8acfe48bf98f1e6e11b0e090d3eb4b5a05b51d76f` | 548,352 |
| `NoHDDUnload.dll` | `ca57064497946b39fbfb445ca8a6e7eecdb7671ba0b3a4e44787de0a5c15227f` | 76,800 |

**Note**: G1 documentation hashes were incorrect. Cache hashes above are authoritative.

## G1 Audit Documents

| Document | Exists |
|----------|--------|
| `docs/GAME_CONTENT_INITIAL_INVENTORY.md` | Yes |
| `docs/GAME_CONTENT_FILE_INVENTORY.md` | Yes |
| `docs/GAME_CONTENT_FORENSIC_FINAL_REPORT.md` | Yes |
| `docs/GAME_NETWORK_ENDPOINT_MAP.md` | Yes |
| `docs/GAME_INPUT_IO_AUDIT.md` | Yes |
| `docs/GAME_STATIC_DEPENDENCY_AUDIT.md` | Yes |
| `docs/GAME_RUNTIME_DEPENDENCIES.md` | Yes |
| `docs/GAME_CONFIGURATION_MAP.md` | Yes |
| `docs/GAME_EXECUTABLE_CANDIDATES.md` | Yes |
| `docs/NO_HDD_UNLOAD_AUDIT.md` | Yes |
| `docs/UE4_GAME_LAYOUT.md` | Yes |
| `docs/CURRENT_CONTROL_MAPPING.md` | Yes |
| `docs/CONTROL_CONFIGURATION_PLAN.md` | Yes |
| `docs/SAFE_FIRST_LAUNCH_PLAN.md` | Yes |
| `docs/generated/game_content_manifest.json` | Yes |
| `docs/generated/game_content_detailed_audit.json` | Yes |
| `docs/generated/game_configs_content.json` | Yes |

## Guards

| Guard | Status |
|-------|--------|
| Matching | NOT_IMPLEMENTED (501) |
| Battle | NOT_IMPLEMENTED (501) |
| Game files modified | No |
| D: drive mapped | No |
| Registry modified | No |
| Services installed | No |
| DNS/hosts modified | No |
| Firewall modified | No |
| Input drivers installed | No |
| DLLs injected | No |
| PAKs extracted | No |
| Copyrighted content in Git | No |

## Pre-Launch State

| Item | State |
|------|-------|
| Port 4000 | Not listening |
| Port 4001 | Not listening |
| Port 6666 | Not listening |
| Port 8000 | Listening (Python/uvicorn, PID varies) |
| AcrGame.exe | Not running |
| AcrGame-Win64-Shipping.exe | Not running |
| NesysService.exe | Not running |
| D: drive | Does not exist |
| SQLite DB | Created (`server/data/starwing.db`) |
| Python server | Running (HTTP on 8000) |
