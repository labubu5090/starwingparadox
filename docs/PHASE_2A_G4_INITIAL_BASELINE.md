# Phase 2A-G4 Initial Baseline

## Git State

- HEAD: `c8a9cc4`
- Branch: `master`
- Working tree: Clean (data/ and game_content_stats.json untracked)

## Running Processes

- No AcrGame processes running
- No NesysService running
- Python server on 127.0.0.1:4001 (PID 45664)
- No processes on 4000, 6666, or 8000

## Game File Hashes (Disk Verified)

| File | SHA-256 |
|------|---------|
| AcrGame.exe | 97800621BB91A2706FBC68AD937679C874B17AC1B2389BDDF472BE9350E62D6C |
| AcrGame-Win64-Shipping.exe | CE4C89054BF7C4D833EE8AF455A485AC401EEAD12A80FFC077663A768FD47DC4 |
| NesysService.exe | 3A968F29B12050DD1B3AE7A8ACFE48BF98F1E6E11B0E090D3EB4B5A05B51D76F |

## Test Results

- 802 collected, 794 passed, 2 failed (pre-existing), 6 skipped
- Pre-existing failures: test_codec_edge_cases, test_tcp_server
- Server health: OK

## Process Monitor

Not installed. Using PowerShell/psutil-based observation.
