# Current Control Mapping

## 1. Input Layers

```
Layer 3: UE4 Input System (Action/Axis Mappings)
  ↓
Layer 2: XInput Gamepad API
  ↓
Layer 1: USBIO Custom Arcade IO
```

## 2. Flight Control Mapping

### Left Pilot

| Action | USBIO Input | Gamepad Input | Keyboard |
|--------|-------------|---------------|----------|
| Left Shot | USBIO_LeftButton | LeftShoulder (L1) | D-pad Left |
| Left Pedal | USBIO_LeftPedal2 | LeftTrigger (L2) | D-pad Down |
| Left Stick X | USBIO LeftStickAxisX | Gamepad_LeftX | — |
| Left Stick Y | USBIO LeftStickAxisY | Gamepad_LeftY | — |
| Left Lever X | USBIO LeftLeverAxisX | — | — |
| Left Lever Y | USBIO LeftLeverAxisY | — | — |

### Right Pilot

| Action | USBIO Input | Gamepad Input | Keyboard |
|--------|-------------|---------------|----------|
| Right Shot | USBIO_RightButton | RightShoulder (R1) | D-pad Right |
| Right Pedal | USBIO_RightPedal1 | RightTrigger (R2) | D-pad Up |
| Right Stick X | USBIO RightStickAxisX | Gamepad_RightX | — |
| Right Stick Y | USBIO RightStickAxisY | Gamepad_RightY | — |
| Right Lever X | USBIO RightLeverAxisX | — | — |
| Right Lever Y | USBIO RightLeverAxisY | — | — |

### Shared

| Action | USBIO Input | Gamepad Input | Keyboard |
|--------|-------------|---------------|----------|
| Step | — | FaceButton_Right (B) | NumPad 1 |
| WeaponChange | — | FaceButton_Top (Y) | NumPad 2 |
| LButton | USBIO_LthumPush | FaceButton_Left (X) | NumPad 0 |
| RButton | USBIO_RthumPush | — | — |

## 3. Menu Navigation

| Action | Gamepad | Keyboard | Test Mode |
|--------|---------|----------|-----------|
| Navigate Up | Left Stick Y Up | Arrow Up | Lever Up |
| Navigate Down | Left Stick Y Down | Arrow Down | Lever Down |
| Navigate Left | Left Stick X Left | Arrow Left | Lever Left |
| Navigate Right | Left Stick X Right | Arrow Right | Lever Right |
| Confirm | RightTrigger | Enter | ENTER switch |
| Back | — | — | TEST switch |

## 4. Cabinet Controls

| Switch | Purpose |
|--------|---------|
| SERVICE | Service mode access |
| TEST | Test mode entry |
| SELECT | Menu selection |
| ENTER | Menu confirmation |
| COIN | Credit input |

## 5. Runtime Observation (Phase 2A-G2)

| Input | Runtime Status |
|-------|----------------|
| XInput | Loaded by bootstrap (XINPUT1_3.dll) — OPERATOR_TEST_REQUIRED |
| Keyboard | UE4 default fallback — OPERATOR_TEST_REQUIRED |
| USBIO | NOT_DETECTED — NESYS service never started |

**Note**: The game did not report any input errors. Default UE4 input configuration was accepted.

## 6. Sensor Inputs

| Sensor | Purpose |
|--------|---------|
| Safety Sensor A | Safety check |
| Safety Sensor B | Safety check |
| Seat Actuator Left | Motion platform |
| Seat Actuator Right | Motion platform |
