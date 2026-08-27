# Process Monitor Observation

## Status

**NOT_AVAILABLE** — Microsoft Process Monitor is not installed on this system.

## Alternative Observation Methods Used

1. **PowerShell Get-Process** — Process inventory
2. **PowerShell Get-NetTCPConnection** — TCP connection monitoring
3. **psutil** — Python-based process and connection monitoring
4. **System.IO.Directory** — Named pipe enumeration
5. **Game log analysis** — AcrGame.log parsing

## Limitations

Without Process Monitor:
- Cannot trace file system operations in real-time
- Cannot trace registry operations
- Cannot trace process creation events with command lines
- Cannot trace named pipe creation/connection events
- Cannot trace DLL loads

## Recommendation

Install Microsoft Sysinternals Process Monitor for future G5 investigation:
- Filter: AcrGame.exe, AcrGame-Win64-Shipping.exe, NesysService.exe
- Operations: Process Create, CreateFile, ReadFile, WriteFile, RegOpenKey, CreatePipe
- Export: CSV with sanitized metadata
