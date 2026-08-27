# D Drive Runtime Observation

## D: Drive State

| Property | Value |
|----------|-------|
| D: exists | **No** |
| Drive type | N/A |
| Volume label | N/A |
| Free space | N/A |
| D:\Saved exists | No |
| D:\GalaxySaved exists | No |
| D:\ACRSaved exists | No |
| Unrelated data | N/A |

## Classification

**D_DRIVE_ABSENT**

D: drive does not exist on this system. The game's `D DRIVE CONTENTS` directory at `X:\StarwingParadox\D DRIVE CONTENTS\` contains the original runtime data but there is no D: drive to map to.

## Implications

- Game may look for save data on D:\
- Game may look for config on D:\
- NoDdrive workaround applied (None — D: is simply absent)
- Dry run will observe whether the game requires D:\ or gracefully handles its absence

## No Action Taken

- No SUBST drive created
- No junction created
- No D: drive modification
- No D DRIVE CONTENTS copied
