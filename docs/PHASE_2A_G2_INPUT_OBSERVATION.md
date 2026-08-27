# Phase 2A-G2 Input Observation

## Input Detection Results

| Input Path | Classification |
|------------|----------------|
| Native XInput controller | OPERATOR_TEST_REQUIRED |
| Keyboard | OPERATOR_TEST_REQUIRED |
| Original USBIO | NOT_DETECTED |
| Missing USBIO | DETECTED — NESYS service never started |
| Trigger axes | CONFIGURED_NOT_RUNTIME_VERIFIED |
| Left/right stick axes | CONFIGURED_NOT_RUNTIME_VERIFIED |
| Menu navigation | OPERATOR_TEST_REQUIRED |
| Coin | OPERATOR_TEST_REQUIRED |
| Start | OPERATOR_TEST_REQUIRED |
| Test | OPERATOR_TEST_REQUIRED |
| Service | OPERATOR_TEST_REQUIRED |

## Observations from Log

- Game detected language: zh-TW (Traditional Chinese), fell back to en
- D3D11 renderer initialized with NVIDIA GeForce RTX 5090
- XInput was loaded by bootstrap (AcrGame.exe imports XINPUT1_3.dll)
- No USBIO device detected (NESYS service never started)
- No input-related errors in log — game accepted default input configuration

## Notes

- The game creates `Input.ini` in AppData on first launch
- The game uses UE4's input mapping system (ActionMappings/AxisMappings)
- USBIO is used by the original arcade cabinet for sticks, buttons, and pedals
- Without NESYS service, the game cannot verify card reader or IO board

## Operator Checklist (Manual Testing Required)

| Test | Action | Expected |
|------|--------|----------|
| XInput | Connect Xbox controller, press buttons | Game responds |
| Keyboard | Press arrow keys + Enter | Menu navigation |
| Window focus | Click game window | Focus gained |
| Close | Press Alt+F4 or close button | Game exits cleanly |
| Test mode | Not available without NESYS | N/A |
