# Game File Hash Manifest

## 1. Cache File Location

`C:\Users\KAHO\Pictures\Starwing\data\file_hash_cache.json`

## 2. Cache Contents

- 37,334 entries (all files in game content)
- SHA-256 hashes
- File sizes

## 3. Key File Hashes

| File | SHA-256 | Size |
|------|---------|------|
| `AcrGame.exe` | `0202fc83f5f8027f641e90196549190a083cd5f3e67e0c83c682beef06ed780e` | 161,280 |
| `AcrGame-Win64-Shipping.exe` | `6c845e7433144b917d1df0d4e3937960ea2970a72ae218916013d0052a09f85a` | 163,440,640 |
| `NesysService.exe` | `06ef9d72478198007435377564d054141039222b4d7243e6c629f7c5c2162f74` | 548,352 |
| `NoHDDUnload.dll` | `3091505950470abdd2e140400c0e04503e5e6b320637393f6214df612d8406f0` | 76,800 |
| `NoHDDUnload.ini` | `bf6e17af8b02dc6a8f7d6ab6f5f9626ef2d226f3f2c2722489dbb08dc03899c6` | 31 |
| `NesysNet.dll` | `5657c4f7811758f67d9521c31d28760e46f93f08e40e2b2a136ca49b678ed6a1` | ~200KB |

## 4. Cache Usage

- Created by `tools/cabinet/collect_game_content_hashes.py`
- Referenced by `app/db/file_hash_store.py`
- Used for game content integrity verification

## 5. Verification

To re-verify a specific file:
```python
import hashlib
path = r"X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe"
with open(path, "rb") as f:
    hash = hashlib.sha256(f.read()).hexdigest()
print(hash)
```

## 6. Known Issues

- Some files (especially in `D DRIVE CONTENTS\`) show identical hashes — likely empty or minimal content
- Pak files are not individually hashed (too large for real-time verification)
