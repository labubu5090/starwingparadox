# Game Input and IO Audit

## 1. Input System Overview

Starwing Paradox uses three layers of input:
1. **USBIO** — Custom arcade cabinet IO (joysticks, buttons, pedals)
2. **XInput Gamepad** — Standard Xbox controller fallback
3. **Keyboard** — Menu navigation fallback

## 2. USBIO Axis Mappings (Cabinet-Specific)

From `DefaultInput.ini`:

| Axis Name | Dead Zone | Sensitivity | Purpose |
|-----------|-----------|-------------|---------|
| `USBIOLeftStickAxisX` | 0.0 | 1.0 | Left stick X |
| `USBIOLeftStickAxisY` | 0.0 | 1.0 | Left stick Y |
| `USBIORightStickAxisX` | 0.0 | 1.0 | Right stick X |
| `USBIORightStickAxisY` | 0.0 | 1.0 | Right stick Y |
| `USBIOLeftLeverAxisX` | 0.0 | 1.0 | Left lever X |
| `USBIOLeftLeverAxisY` | 0.0 | 1.0 | Left lever Y |
| `USBIORightLeverAxisX` | 0.0 | 1.0 | Right lever X |
| `USBIORightLeverAxisY` | 0.0 | 1.0 | Right lever Y |

## 3. USBIO Action Mappings (Cabinet Buttons)

| Action | USBIO Key | Purpose |
|--------|-----------|---------|
| `Dash` | `USBIO_RightPedal1` | Right pedal — dash |
| `Jump` | `USBIO_LeftPedal2` | Left pedal — jump |
| `ShotR` | `USBIO_RightButton` | Right stick button — right shot |
| `ShotL` | `USBIO_LeftButton` | Left stick button — left shot |
| `RButton` | `USBIO_RthumPush` | Right thumb push |
| `LButton` | `USBIO_LthumPush` | Left thumb push |

## 4. Gamepad Action Mappings (XInput)

| Action | Gamepad Key | Purpose |
|--------|-------------|---------|
| `ShotR` | `Gamepad_RightShoulder` | Right shoulder — right shot |
| `Jump` | `Gamepad_LeftTrigger` | Left trigger — jump |
| `Dash` | `Gamepad_RightTrigger` | Right trigger — dash |
| `ShotL` | `Gamepad_LeftShoulder` | Left shoulder — left shot |
| `LButton` | `Gamepad_FaceButton_Left` | Face left (X) |
| `Step` | `Gamepad_FaceButton_Right` | Face right (B) |
| `WeaponChange` | `Gamepad_FaceButton_Top` | Face top (Y) |

## 5. Keyboard Fallback

| Action | Key | Purpose |
|--------|-----|---------|
| ShotR | D-pad Right | Right shot |
| Jump | D-pad Down | Jump |
| Dash | D-pad Up | Dash |
| ShotL | D-pad Left | Left shot |
| LButton | NumPad 0 | Left button |
| Step | NumPad 1 | Step |
| WeaponChange | NumPad 2 | Weapon change |
| MenuNavigation | Arrow keys + Enter | Menu navigation |

## 6. Cabinet Physical Controls (from test mode JSON)

| Control | Description |
|---------|-------------|
| SERVICE switch | Service mode access |
| TEST switch | Test mode entry |
| SELECT switch | Menu selection |
| ENTER switch | Menu confirmation |
| COIN switch | Credit input |

## 7. Cabinet Hardware (from test mode JSON)

| Hardware | Description |
|----------|-------------|
| Left joystick | Flight stick (left player) |
| Right joystick | Flight stick (right player) |
| Left pedal | Jump pedal |
| Right pedal | Dash pedal |
| NESiCA card reader | IC card reader |
| Touch panel | Sub-monitor touch |
| Seat actuator (left) | Motion platform |
| Seat actuator (right) | Motion platform |
| Safety sensors A/B | Safety sensors |
| LED lamps | Cabinet lighting |
