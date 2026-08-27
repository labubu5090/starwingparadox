# NESYS Offline Block — Correction Notice

## Date: 2026-08-27

## Previous Misinterpretation

The G4 and earlier phases incorrectly described the game reaching "InsertStart" as a
**usable title state** waiting normally for coin/start input.

This interpretation was **disproven by repeated physical runtime observation** by the operator.

## Corrected Interpretation

The game repeatedly reaches a screen displaying:

- 現在オフラインの為チェック出来ません。
  (The system is currently offline and cannot perform the check.)
- オンラインになるまでお待ちください。
  (Wait until the system becomes online.)
- 現在オフラインモードの為カードを使ったプレイはできません
  (Card-based gameplay is unavailable because the game is in offline mode.)
- CREDIT(S) 0

This is **NOT** a normal InsertStart state. The game is blocked by NESYS being offline.

## Verified Current State

| Item | Status |
|------|--------|
| HTTP server discovery | VERIFIED_WORKING |
| Matching server address response | VERIFIED_RECEIVED |
| NESYS status | OFFLINE |
| Card play | BLOCKED_BY_NESYS_OFFLINE |
| Normal game flow | NOT_REACHED |
| Coin/start validation | NOT_YET_VALID |
| Matching | NOT_IMPLEMENTED |
| Battle | NOT_IMPLEMENTED |
| Real playability | NOT_PROVEN |
| Primary blocker | NESYS_SERVICE_INITIALIZATION |

## Impact on Historical Reports

G4 and earlier reports that describe InsertStart as a usable state are **incorrect**.
Those reports should be understood as describing the **log sequence** (SystemDataCheck →
PromotionMovie → InsertStart widget visible), NOT as describing a **playable state**.

The game does reach the InsertStart widget, but it is immediately overlaid by the NESYS
offline error screen. The game cannot proceed beyond this point without NESYS initialization.

## Root Cause

The game requires NesysService.exe to be running and initialized before it will transition
from offline to online mode. NesysService.exe exits immediately (code -1) when launched
standalone, indicating it requires a specific launch context, arguments, or parent process.

Without NESYS initialization:
- Card-based gameplay is unavailable
- The game remains in offline/testmode
- Normal game flow is not reached
- Coin/start input cannot be validated
