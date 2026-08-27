# Control Configuration Plan

## 1. Current Status

| Component | Status |
|-----------|--------|
| UE4 Input Mappings | Defined in DefaultInput.ini |
| USBIO Axis Mappings | Defined (8 axes) |
| USBIO Button Mappings | Defined (6 buttons) |
| Gamepad Fallback | Defined (XInput) |
| Keyboard Fallback | Defined |
| Test Mode Config | Defined (tm_switch.json, tm_main.json) |

## 2. Unknown Fields (6 Fields)

From player profile data:

| Field | Type | Possible Purpose |
|-------|------|------------------|
| UnknownBool1 | bool | Unknown flag |
| UnknownBool2 | bool | Unknown flag |
| UnknownInt1 | int | Unknown value |
| UnknownInt2 | int | Unknown value |
| UnknownString1 | string | Unknown data |
| UnknownString2 | string | Unknown data |

**Recommendation**: These fields need runtime analysis to determine their purpose.

## 3. Proposed Configuration System

### Phase 2A (Current)

| Task | Status |
|------|--------|
| Document UE4 input mappings | Complete |
| Document USBIO mappings | Complete |
| Document test mode config | Complete |
| Create safe launch plan | Complete |
| Create game content audit | In Progress |

### Phase 2B (Future)

| Task | Description |
|------|-------------|
| Implement USBIO emulation | Create virtual USBIO device |
| Implement XInput passthrough | Map physical gamepad to UE4 |
| Implement test mode API | Expose test mode via REST |
| Implement seat control API | Control motion platform via REST |
| Implement sensor API | Read safety sensors via REST |
| Implement LED control API | Control cabinet lighting via REST |

## 4. Configuration Storage

### Current

- UE4 configs: `WindowsNoEditor\AcrGame\Config\*.ini`
- Runtime configs: `D DRIVE CONTENTS\Saved\*`
- Test mode configs: `WindowsNoEditor\AcrGame\Content\TestMode\SettingFile\*.json`

### Proposed

- **Do NOT modify** existing configs
- **Overlay system**: Create `config/game/` directory for custom configs
- **Runtime injection**: Use DLL hooking to inject custom configs at runtime

## 5. Input Mapping Strategy

### For Development (No Cabinet)

| Priority | Input | Mapping |
|----------|-------|---------|
| 1 | XInput Gamepad | Map to USBIO axes/buttons |
| 2 | Keyboard | Map to menu navigation |
| 3 | Mouse | Map to touch panel |

### For Cabinet

| Priority | Input | Mapping |
|----------|-------|---------|
| 1 | USBIO | Direct passthrough |
| 2 | NESiCA Reader | Direct passthrough |
| 3 | Seat Actuators | Direct passthrough |
