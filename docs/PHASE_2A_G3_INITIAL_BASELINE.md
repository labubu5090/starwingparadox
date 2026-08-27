# Phase 2A-G3 Initial Baseline

## Git State

| Item | Value |
|------|-------|
| HEAD | `9dabca9` |
| Branch | master |
| Working tree | Clean (untracked: `data/`, `docs/generated/game_content_stats.json`) |

## Game File Hashes

| File | SHA-256 |
|------|---------|
| AcrGame.exe | `97800621bb91a2706fbc68ad937679c874b17ac1b2389bddf472be9350e62d6c` |
| AcrGame-Win64-Shipping.exe | `ce4c89054bf7c4d833ee8af455a485ac401eead12a80ffc077663a768fd47dc4` |
| NesysService.exe | `3a968f29b12050dd1b3ae7a8acfe48bf98f1e6e11b0e090d3eb4b5a05b51d76f` |
| NoHDDUnload.dll | `ca57064497946b39fbfb445ca8a6e7eecdb7671ba0b3a4e44787de0a5c15227f` |

## G2 Runtime Evidence

| Item | Value |
|------|-------|
| Bootstrap launched | Yes (PID 10976) |
| Shipping launched | Yes (PID 10480) |
| NesysService started | No |
| CertErrors | 5131 in ~130 seconds (~39/sec) |
| First CertError | t=4s after launch |
| NESYS setup | Completed at t=2s |
| External connection | 44.213.205.183:443 (HTTPS) |
| Asset preload | 5132/7553 at t=60s |
| AppData files created | 13 |

## Listeners

| Port | Status |
|------|--------|
| 4000 | Free |
| 4001 | Free |
| 6666 | Free |
| 8000 | Listening (Python, PID 25692) |

## Processes

| Name | PID | Status |
|------|-----|--------|
| python (venv) | 25692 | Running (old server) |
| AcrGame* | — | Not running |
| NesysService* | — | Not running |

## Guards

| Guard | Status |
|-------|--------|
| Matching | NOT_IMPLEMENTED (501) |
| Battle | NOT_IMPLEMENTED (501) |
| Game files modified | No |
| D: drive mapped | No |
| No port-4000 fake service | PASS |
