# Phase 2A-G12 Initial Baseline

**Phase**: 2A-G12  
**Date**: 2026-08-28  
**Status**: VERIFIED  

---

## Git State

| Metric | Value |
|--------|-------|
| Current HEAD | `58e9934` |
| Branch | master |
| Working tree | clean (no staged changes) |
| Untracked files | docs/generated/g9-run-a/, docs/generated/tcp_connected_vs_http_only.json, tools/game/procmon/, tools/game/run-g9-three-delays.ps1 |
| Modified files | docs/generated/g5_proxy_requests.jsonl, tools/game/g9_analyze_log.py (deleted) |

### Commit Verification

| Commit | Message | Verified |
|--------|---------|----------|
| `99f55ed` | docs: complete upstream repository launch instructions audit | YES |
| `58e9934` | docs: update PROGRESS.md with G11 upstream audit results | YES |
| `5388190` | docs: establish Starwing OpenKey provenance boundary | YES |
| `d8b7c6c` | fix: load generated protobuf for Starwing TCP runtime | YES |
| `132530f` | fix: stabilize initial Starwing TCP protocol handling | YES |

---

## G11 Documents Verification

| Document | Path | Exists |
|----------|------|--------|
| Upstream Audit | docs/UPSTREAM_LAUNCH_INSTRUCTIONS_AUDIT.md | YES |

---

## legacy-js Status

| Metric | Value |
|--------|-------|
| Location | C:\Users\KAHO\Pictures\Starwing\legacy-js |
| Remote origin | https://github.com/ArcadeMachinist/StarwingParadox.git |
| Current commit | 020adaf |
| Local modifications | NONE |
| Working tree | clean |

---

## Game Content Verification

| File | Path | Size | Last Write |
|------|------|------|------------|
| AcrGame.exe | X:\StarwingParadox\WindowsNoEditor\AcrGame.exe | 161,280 | 30/9/2020 8:54:04 |
| AcrGame-Win64-Shipping.exe | X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe | 163,119,104 | 30/9/2020 8:56:12 |
| NesysService.exe | X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe | 548,352 | 23/3/2018 17:55:00 |

### SHA-256 Hashes

| File | SHA-256 |
|------|---------|
| AcrGame.exe | `97800621BB91A2706FBC68AD937679C874B17AC1B2389BDDF472BE9350E62D6C` |
| AcrGame-Win64-Shipping.exe | `CE4C89054BF7C4D833EE8AF455A485AC401EEAD12A80FFC077663A768FD47DC4` |
| NesysService.exe | `3A968F29B12050DD1B3AE7A8ACFE48BF98F1E6E11B0E090D3EB4B5A05B51D76F` |

---

## Runtime Database

| Metric | Value |
|--------|-------|
| Database file | server/data/starwing.db |
| Staged | NO |
| Tables | 17 (via Alembic) |

---

## Key/Certificate Material

| Metric | Value |
|--------|-------|
| Staged | NO |
| OpenKey files | D DRIVE CONTENTS only (read-only) |
| Certificate files | NONE found |
| Registry entries | NONE created |

---

## D: Drive Mapping

| Metric | Value |
|--------|-------|
| Active | NO |
| Last known mount | NOT_MOUNTED |

---

## Test Baseline

| Metric | Value |
|--------|-------|
| Tests collected | 835 |
| Tests passed | 834 |
| Tests skipped | 1 |
| Tests failed | 0 |
| Warnings | 209 (aiosqlite event loop cleanup) |

---

## Static Analysis

| Tool | Version | Result |
|------|---------|--------|
| Ruff | - | 0 errors |
| Mypy | 2.3.1 | 0 errors on 64 source files |

---

## Conclusion

All baseline checks pass. Ready for G12 artifact search.
