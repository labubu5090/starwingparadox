# D: Drive Test Tooling

## Purpose
Reconstruct the D: drive runtime environment for Starwing Paradox using a temporary VHDX.

## Safety
- Uses a dedicated VHDX file in `data/starwing-test-d.vhdx`
- No impact on physical disks
- No impact on X: game files
- No automatic startup persistence
- No registry modification
- No binary modification

## Scripts

| Script | Purpose |
|--------|---------|
| `create-starwing-test-vhd.ps1` | Create the VHDX file |
| `mount-starwing-test-vhd.ps1` | Mount VHDX as D: |
| `populate-starwing-test-vhd.ps1` | Copy D DRIVE CONTENTS to D: |
| `verify-starwing-test-vhd.ps1` | Verify D: contents |
| `dismount-starwing-test-vhd.ps1` | Safely dismount D: |
| `remove-starwing-test-vhd.ps1` | Remove VHDX file |

## Usage

```powershell
# 1. Create VHDX
.\create-starwing-test-vhd.ps1

# 2. Mount as D:
.\mount-starwing-test-vhd.ps1

# 3. Populate from source
.\populate-starwing-test-vhd.ps1

# 4. Verify
.\verify-starwing-test-vhd.ps1

# 5. Test NesysService
# ...

# 6. Dismount
.\dismount-starwing-test-vhd.ps1

# 7. Remove (optional)
.\remove-starwing-test-vhd.ps1
```

## Notes
- VHDX is dynamically expanding (starts small, grows up to 50MB max)
- All files copied from `X:\StarwingParadox\D DRIVE CONTENTS`
- OpenKey.json is copied but never logged or committed
