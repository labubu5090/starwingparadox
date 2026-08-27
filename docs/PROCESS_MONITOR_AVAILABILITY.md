# Process Monitor Availability

## Date: 2026-08-27

## Status: PROCMON_NOT_AVAILABLE

## Search Results

| Location | Found |
|----------|-------|
| PATH | No |
| C:\Tools\ | No |
| C:\Sysinternals\ | No |
| Program Files | No |
| User Desktop | No |
| User Downloads | No |
| Project tools/ | No |
| SysinternalsSuite | No |

## Requirements

Process Monitor (Procmon64.exe) is needed to trace NesysService initialization
and identify the exact failure point.

## Required Version
- Microsoft Sysinternals Process Monitor
- x64 architecture (NesysService is x64)
- Latest version preferred

## Elevation Required
Yes — Process Monitor requires administrator privileges to capture system events.

## EULA
Process Monitor requires accepting Microsoft Sysinternals EULA on first run.
This must be accepted by the operator.

## Recommended Installation

Option 1: Download from Microsoft
- https://learn.microsoft.com/en-us/sysinternals/downloads/procmon
- Extract to C:\Tools\ or similar

Option 2: Package manager
```
winget install Microsoft.Sysinternals.ProcessMonitor
```

## Next Steps

Once Process Monitor is available:
1. Accept EULA
2. Run as administrator
3. Follow the capture plan in PROCMON_NESYSSERVICE_CAPTURE_PLAN.md
