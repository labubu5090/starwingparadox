# Original Cabinet Provisioning Flow

**Date:** 2026-08-28

## Evidence-Based Flow

### Proven Local Steps

| Step | Component | Evidence | Status |
|------|-----------|----------|--------|
| 1. Game installation | AcrGame-Win64-Shipping.exe | File exists at WindowsNoEditor\AcrGame\Binaries\Win64\ | COMPLETED |
| 2. D: drive content | D DRIVE CONTENTS directory | 217 files, 7.9 MB | COMPLETED |
| 3. NesysService.exe | D:\system\Service\NesysService.exe | 548,352 bytes | PRESENT |
| 4. OpenKey.json | D:\Saved\ACRSaved\SaveData\OpenKey.json | 96 bytes | PRESENT |
| 5. SaveData.json | D:\Saved\ACRSaved\SaveData\SaveData.json | Present in D DRIVE CONTENTS | PRESENT |

### Strong Inference

| Step | Component | Evidence | Status |
|------|-----------|----------|--------|
| 6. D: drive mounting | VHD or physical drive | populate-starwing-test-vhd.ps1 | REQUIRED |
| 7. Launcher process | Unknown launcher | NesysService expects parent context | REQUIRED |
| 8. NESYS certificates | Windows certificate store | NesysService uses CertOpenStore | REQUIRED |
| 9. Registry configuration | Machine-specific keys | NesysService uses RegOpenKeyExA | REQUIRED |
| 10. Network access | cert3.nesys.jp | NesysService connects to TAITO servers | REQUIRED |

### Unknown External Steps

| Step | Component | Evidence | Status |
|------|-----------|----------|--------|
| 11. Factory provisioning | Unknown tool | OpenKey.json origin unknown | UNKNOWN |
| 12. Cabinet registration | NESYS enrollment | NesysService authenticates cabinet | UNKNOWN |
| 13. Service startup | Launcher/startup script | NesysService expects command-line args | UNKNOWN |
| 14. Certificate provisioning | TAITO servers | cert3.nesys.jp authentication | UNKNOWN |
| 15. Network configuration | Cabinet network | External service access | UNKNOWN |

### Sensitive Authentication Boundary

| Step | Component | Evidence | Status |
|------|-----------|----------|--------|
| 16. NESYS authentication | cert3.nesys.jp | Certificate verification | AUTHENTICATION_BOUNDARY |
| 17. NESICA card service | fjm170920zero.nesica.net | Card authentication | AUTHENTICATION_BOUNDARY |
| 18. OpenKey generation | Unknown | Content sensitive | AUTHENTICATION_BOUNDARY |

## Provisioning Chain (Inferred)

```
FACTORY/CABINET SETUP:
  1. Install AcrGame-Win64-Shipping.exe
  2. Deploy D: drive contents (217 files)
  3. Install NesysService.exe
  4. Provision OpenKey.json (origin unknown)
  5. Configure certificates (Windows cert store)
  6. Configure registry keys
  7. Set up network access

BOOT SEQUENCE:
  8. Launcher starts NesysService.exe
  9. NesysService creates named pipe
  10. NesysService contacts cert3.nesys.jp
  11. NesysService authenticates cabinet
  12. Game connects to named pipe
  13. Game reads OpenKey.json
  14. Game checks NESYS status
  15. SystemDataCheck passes
  16. Game proceeds to online mode
```

## Missing on This System

| Component | Status | Impact |
|-----------|--------|--------|
| Launcher process | MISSING | NesysService cannot start |
| NESYS certificates | MISSING | Authentication fails |
| Registry keys | MISSING | Configuration missing |
| Network access | UNKNOWN | External services unreachable |
| OpenKey.json (runtime) | MISSING_AT_EXPECTED_PATH | SystemDataCheck fails |

## Conclusion

PROVISIONING_STATUS: ORIGINAL_PROVISIONING_CONTEXT_MISSING

The original cabinet provisioning flow requires external components (launcher, certificates, registry, network) that are not present on this system. OpenKey.json exists in D DRIVE CONTENTS but cannot be used without the full provisioning context.
