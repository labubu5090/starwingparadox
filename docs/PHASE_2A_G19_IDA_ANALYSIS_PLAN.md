# Phase 2A-G19 IDA / PE Static Analysis Plan

## Status

**Classification:** EVALUATED_WITH_PEFILE (IDA batch/headless mode unavailable)

## Purpose

Document the static-analysis approach used to extract game-client-visible contracts from the
Starwing Paradox cabinet executables and DLLs for the private-server minimum-contract study.

## Analysis Tooling Decision

- **Intended:** IDA Pro 9.3 batch mode (`idat.exe`) for disassembly-level control-flow (RVAs, XREFs).
- **Actual result:** `idat.exe` failed with `Failed to initialize IDA as library (error code 2)`;
  `ida.exe` in batch mode completed with no output.
- **Substitute used:** `pefile` Python library at `tools/ida/pe_analysis.py` plus companion
  string/source-path extraction helpers. This recovers imports, exports, sections, and strings
  but NOT disassembly-level RVAs or control-flow. RVAs remain `UNKNOWN` where not confirmed.

## Executables and DLLs Analyzed

| Artifact | Role | Imports (DLLs) | Key finding |
|----------|------|----------------|-------------|
| AcrGame-Win64-Shipping.exe | Main game (163 MB) | 860 funcs / 46 DLLs | HTTP (WININET/WINHTTP), TCP (WS2_32), pipe primitives, Lua, protobuf strings |
| AcrGame.exe | Launcher (161,280 B) | 81 funcs / 4 DLLs | CreateProcessW/ShellExecuteExW/LoadLibraryW launcher role |
| GALAXYIO.dll | Card I/O (154,112 B) | 104 funcs / 5 DLLs | WinHTTP client; `https://cert2.nesys.jp`; AMIC card endpoint; WINUSB + SETUPAPI |
| Lua524.dll | Scripting (231,936 B) | 119 funcs / 12 DLLs | 147 Lua exports |
| QRreader.dll | QR reading (770,048 B) | 84 funcs / 4 DLLs | 5 exports (Open 1000, Close 1001, GetState 1002, GetBuffer 1003, GetCode 1004) |

## Analysis Steps

1. **Import table extraction** (`extract_imports.py`) — network, pipe, crypto, scripting APIs.
2. **String extraction** (`extract_strings.py`) — ASCII + Unicode, 1,135,629 + 653,911 strings in the main game.
3. **Source-path extraction** (`extract_source_paths.py`) — 378 paths revealing module structure.
4. **Protocol string extraction** (`extract_protocol_strings.py`) — HTTP endpoint, TCP command, NESYS command,
   and error-handling strings.
5. **Pattern search** (`search_patterns.py`) — `\\.\pipe\`, pipe API usage, certificate endpoints.
6. **Module-specific analysis** (`analyze_galaxyio.py`, `analyze_acrgame_launcher.py`) — dominated DLL/layer behaviors.

## Outputs

- `tools/ida/pe_analysis_results.json`
- `tools/ida/string_analysis_results.json`
- `tools/ida/source_paths.json`
- `artifacts/phase_2a_g19/*.json` (module map, dependency graph, pipe contract, command dispatch, endpoint classification)

## Limitations

- No disassembly-level control-flow or accurate RVAs (IDA headless unavailable).
- Pipe role (server vs client) unresolved from imports alone; requires control-flow to confirm.
- String-derived command names are name-level identification only; numeric IDs/payloads unconfirmed.

## Next Steps

1. Resolve pipe role and exact frame/payload format via capture or control-flow.
2. Confirm numeric protocol IDs for the protocol-identified commands.
3. Confirm HTTP request/response JSON contracts for the Bind* endpoints.
