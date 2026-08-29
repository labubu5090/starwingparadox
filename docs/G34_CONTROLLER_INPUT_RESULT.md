# G34 Controller Input and Matching Config Result

## Classification
- Controller: JOYCPL_INPUT_CONFIRMED_DIAGNOSTIC_API_GAP
- Matching: MATCHING_INITIALIZATION_STILL_BLOCKED

## Executive Summary
The 8BitDo Ultimate 2C Wireless Controller is recognized by Windows (joy.cpl shows OK status) and readable via the Windows joystick API (winmm), but UE4's Gamepad input path does not activate for this device. XInput reports all 4 slots as ERROR_DEVICE_NOT_CONNECTED. HID opens the device but returns 0 reports. The game's MatchingServer address is resolved via HTTP discovery and TCP connects successfully, but the MatchingServer object requires NesysControl initialization (IsOnline[0]).

## Controller Evidence

### joy.cpl Status
- Device: 8BitDo Ultimate 2C Wireless Controller
- Status: OK (operator-confirmed via screenshot)
- joy.cpl present: Yes

### Windows Joystick API (winmm)
- Device 0: CONNECTED
- Neutral state: X=32767 Y=32767 (centered)
- joyGetPosEx returns JOYERR_NOERROR
- Live input changes detected when controller is physically moved

### HID
- Usage page: 0x0001, Usage: 0x0005 (Game Pad)
- Device opens successfully
- Returns 0 input reports (non-blocking read, 5s timeout)
- Feature reports fail (read error)

### XInput (xinput1_4.dll)
- Slot 0: ERROR_DEVICE_NOT_CONNECTED (1167)
- Slot 1: ERROR_DEVICE_NOT_CONNECTED (1167)
- Slot 2: ERROR_DEVICE_NOT_CONNECTED (1167)
- Slot 3: ERROR_DEVICE_NOT_CONNECTED (1167)

### PnP
- USB Input Device | HIDClass | OK
- HID-compliant game controller | HIDClass | OK

### Raw Input
- 0 devices found (may require elevated permissions)

### DirectInput
- dinput8.dll loadable

### Game Input Path
The game uses three input paths:
1. **Gamepad** (UE4): Gamepad_LeftX/Y, Gamepad_FaceButton_*, etc.
2. **USBIO** (arcade): USBIO_LeftStickAxisX/Y, USBIO_LeftPedal2, etc.
3. **Keyboard/Mouse**: W/A/D, SpaceBar, LeftShift, Q/E, etc.

The game has native UE4 Gamepad action mappings but does not detect the 8BitDo as a Gamepad device.

## Matching Config Evidence

### HTTP Discovery
- Game sends POST to /mock/matching/server
- Proxy strips /mock, forwards to 127.0.0.1:4001
- Python server returns {"ip_addr":"127.0.0.1:6666"}
- Game accepts: _IsSuccess[1] IPAddress[127.0.0.1:6666]

### TCP Connection
- Game connects to 127.0.0.1:6666
- TCP establishes successfully
- Ping (0x66) exchange works every ~20s
- Pong response sent correctly

### MatchingServer Object
- Error persists: "Error No MatchingServer so initialize Nesys before."
- IsOnline[0] — NesysControl not initialized
- Config path bypasses address resolution but NOT object creation gate
- This is a security boundary

### DefaultGame.ini Modifications
- Added [/Script/NetworkModule.NetworkConfig] section
- DefaultMatchingServerAddress=127.0.0.1:6666
- DefaultHttpServerAddress=127.0.0.1:4001
- Backup at DefaultGame.ini.backup-g34

## Controller Remediation
- Selected: OPTION B — Project-owned controller-to-keyboard mapper
- API: Windows joystick API (winmm)
- Application: tools/controller_mapper/mapper_app.py
- Configuration: config/controller_mapping.json
- Mapper provides: Assign buttons, Test Input mode, Emergency Stop
- Adapter defaults disabled
- Only sends approved keyboard keys

## Approved Keyboard Controls
- W = forward
- A = left
- D = right
- Space = foot pedal
- Shift = dash
- Q = left button
- E = right button
- LCtrl = step
- F = AR skill
- Enter = start
- Z = credit
- LMB = shot left
- RMB = shot right
- MMB = weapon change

## Quality Gates
- Tests: 1115 passed, 1 skipped
- Ruff: passed
- Protected hashes: unchanged
- OpenKey: unchanged
- hosts mapping: unchanged
- adapter disabled by default
- no driver installation
- no firmware update
- no DLL injection
