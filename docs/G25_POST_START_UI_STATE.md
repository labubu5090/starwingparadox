# G25 Post-Start UI State

## State After ENTER
- Title screen unchanged
- WBP_InsertStart animation still playing
- No card/player/session state entered
- No error dialog shown
- No network error shown

## Credit System Evidence
- StartCredit: 2 (required)
- Current credits: 0 (available)
- Credit source: NesysService machine data
- Conclusion: Credits gate the Start button

## Card System
- ReadCardMain::ClearPlayerInfo called
- MatchingMain::Clear called
- Systems initialized but no data

## Implication
The game is an arcade cabinet. Without credits from NesysService, the title screen cannot advance. A private server must implement a local credit system.
