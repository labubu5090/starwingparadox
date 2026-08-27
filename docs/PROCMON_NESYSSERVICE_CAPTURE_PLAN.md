# Procmon NesysService Capture Plan

## Date: 2026-08-27

## Objective

Trace NesysService.exe initialization to identify the exact failure point causing
exit code -1.

## Filters

### Process Name Filter (Include)
- `NesysService.exe`

### Operation Categories (Include)
- Process Start/Create/Exit
- Thread Create/Exit
- Load Image (DLL loads)
- CreateFile, QueryOpen, ReadFile, WriteFile, CloseFile
- QueryInformationFile, QueryDirectory, CreateFileMapping
- RegOpenKey, RegCreateKey, RegQueryKey, RegQueryValue, RegSetValue, RegCloseKey
- TCP Connect, TCP Send, TCP Receive, UDP Send, UDP Receive
- Named pipe operations

### Path Filters (Include)
- `*\NesysService.exe*`
- `*\nesys_games*`
- `\\.\pipe\*`
- `\Device\NamedPipe\*`
- `D:\*`
- `C:\Windows\System32\*` (for DLL loads)

### Result Filters (Include for analysis)
- NAME NOT FOUND
- PATH NOT FOUND
- ACCESS DENIED
- REPARSE
- BUFFER OVERFLOW
- NO SUCH FILE
- SHARING VIOLATION
- INVALID PARAMETER
- END OF FILE
- PIPE NOT AVAILABLE
- PIPE BUSY
- DLL NOT FOUND
- DEVICE NOT READY

## Capture Sequence

### Run A: Without D: Drive
1. Ensure D: is not mounted
2. Start Process Monitor capture
3. Launch NesysService.exe from `D:\system\Service\` (via subst or direct path)
4. Wait for exit (typically <2 seconds)
5. Continue capture for 2 seconds post-exit
6. Stop capture
7. Save PML to `C:\Users\KAHO\AppData\Local\Temp\g7_run_a.pml`
8. Export sanitized CSV to `docs/generated/g7_nesys_without_d_sanitized.csv`

### Run B: With D: Drive
1. Mount D: drive using subst
2. Verify D: contents
3. Clear Process Monitor display
4. Start Process Monitor capture
5. Launch NesysService.exe from `D:\system\Service\`
6. Wait for exit
7. Continue capture for 2 seconds post-exit
8. Stop capture
9. Save PML to `C:\Users\KAHO\AppData\Local\Temp\g7_run_b.pml`
10. Export sanitized CSV to `docs/generated/g7_nesys_with_d_sanitized.csv`
11. Dismount D:

### Run C: Game Context (Optional)
1. Clear Process Monitor display
2. Add AcrGame.exe and AcrGame-Win64-Shipping.exe to process filter
3. Start capture
4. Launch AcrGame.exe
5. Wait for NESYS error screen
6. Stop capture
7. Save PML to `C:\Users\KAHO\AppData\Local\Temp\g7_run_c.pml`

## Analysis Points

### Terminal Failure Window
- Last 500ms before process exit
- Last 100 events
- Last failed operation
- Last successful operation
- Last loaded DLL
- Last Registry query
- Last file lookup
- Last pipe operation
- Last network event

### DLL Load Analysis
- All Load Image events
- DLL paths and load results
- Architecture (x86 vs x64)
- Missing dependencies
- Search-order failures

### Registry Analysis
- All RegOpenKey/RegQueryValue events
- Key paths and value names
- Results (found/not found)
- Timing relative to exit

### Certificate Analysis
- Crypt32.dll loads
- CertOpenStore calls
- Certificate store paths
- Certificate-related Registry paths

### Pipe Analysis
- Named pipe creation attempts
- Pipe path access
- Pipe open/connect/disconnect events

## Safety Notes

- Raw PML files are NOT committed to git
- Sensitive CSV/XML exports are NOT committed
- OpenKey values are NOT logged
- No Registry values are created
- No certificates are installed
- No binaries are patched
