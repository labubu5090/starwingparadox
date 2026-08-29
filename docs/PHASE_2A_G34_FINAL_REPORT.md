# Phase 2A G34 Final Report

## Date: 2026-08-29

## Classification
- **Controller**: JOYCPL_INPUT_CONFIRMED_DIAGNOSTIC_API_GAP
- **Matching**: MATCHING_INITIALIZATION_STILL_BLOCKED

## Executive Summary

### Controller Investigation
The 8BitDo Ultimate 2C Wireless Controller is recognized by Windows Game Controllers (joy.cpl) with OK status. The Windows joystick API (winmm) successfully reads device 0 with neutral stick values at X=32767 Y=32767. However, the UE4 Gamepad input path does not detect this device, XInput reports all 4 slots as ERROR_DEVICE_NOT_CONNECTED, and HID opens the device but returns 0 input reports.

The game has native UE4 Gamepad action mappings in DefaultInput.ini but they remain inactive because the controller is not exposed as an XInput or UE4 Gamepad device to the engine.

**Selected Remediation**: OPTION B — Project-owned controller-to-keyboard mapper using the Windows joystick API (winmm).

### Matching Configuration
The game successfully resolves the MatchingServer address via HTTP discovery (127.0.0.1:6666) and establishes a TCP connection with working Ping/Pong exchange. However, the MatchingServer object itself requires NesysControl initialization (`IsOnline[0]`), which remains blocked.

The Config path in DefaultGame.ini (`[/Script/NetworkModule.NetworkConfig]`) bypasses address resolution but does not bypass the MatchingServer object creation gate. This is a security boundary.

## Deliverables

### Controller Mapper
- `tools/controller_mapper/mapper_app.py` — Main GUI application
- `tools/controller_mapper/config.py` — Configuration schema and I/O
- `tools/controller_mapper/joystick.py` — Windows joystick API reader
- `tools/controller_mapper/keyboard_output.py` — Safe keyboard output
- `tools/controller_mapper/process_guard.py` — Foreground window detection
- `config/controller_mapping.json` — Mapping configuration (versioned)

### Documentation
- `docs/G34_CONTROLLER_INPUT_RESULT.md` — Controller input result
- `docs/G34_SIMPLE_CONTROLLER_MAPPER.md` — Mapper usage guide (if created)
- `docs/G34_MATCHING_CONFIG_RESULT.md` — Matching config result

### Artifacts
- `artifacts/phase_2a_g34/controller_windows_inventory.json`
- `artifacts/phase_2a_g34/controller_live_api_result.json`
- `artifacts/phase_2a_g34/game_config_input_analysis.json`
- `artifacts/phase_2a_g34/game_input_path.json`
- `artifacts/phase_2a_g34/controller_remediation.json`
- `artifacts/phase_2a_g34/controller_mapper_result.json`
- `artifacts/phase_2a_g34/matching_runtime_result.json`
- `artifacts/phase_2a_g34/g35_decision.json`
- `artifacts/phase_2a_g34/test_reconciliation.json`
- `artifacts/phase_2a_g34/safety_results.json`

### Tests
- `server/tests/test_g34_controller_mapper.py` — 37 tests

## Quality Gates
- **Tests**: 1115 passed, 1 skipped, 0 failed
- **Ruff**: passed
- **Protected hashes**: unchanged
- **OpenKey**: unchanged
- **hosts mapping**: unchanged

## Safety Confirmation
- No driver installation
- No firmware update
- No DLL injection
- No game patching
- No XInput Plus/x360ce/ViGEm
- No global keyboard hook
- No output to non-Starwing windows
- Adapter disabled by default
- All keys released at shutdown
- Credit safety: max 2 per arm, cooldown, debounce

## G35 Action
1. Investigate NesysControl::IsOnline path to determine if stubbing is possible
2. Operator to test controller mapper with physical controller
3. Consider running mapper_app.py to verify live input mapping
