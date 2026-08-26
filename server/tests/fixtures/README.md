# Test Fixtures

## Status: SYNTHETIC / LEGACY_REFERENCE

No real cabinet captures exist yet. All current fixtures are **synthetic** (generated for testing) or **legacy_reference** (extracted from the legacy JavaScript server code and documentation).

## Current Fixtures

### Synthetic Fixtures
- `sample_battle_result` — Synthetic battle result JSON matching the format from `API-NOTES.txt`
- `sample_player_id`, `sample_nesys_id` — Synthetic player identifiers
- `sample_match_id`, `sample_stage_id` — Synthetic match/stage identifiers

### Legacy Reference Fixtures
- Player IDs 10010 and 10011 — From `paradox.sql` test data
- Match result format — From `API-NOTES.txt` captured request/response
- Ranking data format — From `battleRecorder.js` response structure

## Captures Needed

The following real cabinet captures are needed to validate the Python implementation:

| Capture | Priority | Description |
|---------|----------|-------------|
| `matching_server_request.json` | HIGH | HTTP request to `/matching/server` from real cabinet |
| `matching_server_response.json` | HIGH | HTTP response from `/matching/server` |
| `tcp_connect_handshake.bin` | HIGH | Raw TCP connection and first packet |
| `request_entry_matching.bin` | HIGH | messageType 200 from real cabinet |
| `response_entry_matching.bin` | HIGH | messageType 201 response |
| `notify_match_made.bin` | HIGH | messageType 302 from server |
| `notify_match_begin.bin` | HIGH | messageType 304 from server |
| `battle_record_2on2_request.json` | HIGH | HTTP POST to `/battle/record_2on2` |
| `battle_record_2on2_response.json` | HIGH | HTTP response from `/battle/record_2on2` |
| `burst_entry_request.bin` | MEDIUM | messageType 208 from real cabinet |
| `burst_room_create.bin` | MEDIUM | messageType 210 from real cabinet |
| `burst_room_list.bin` | MEDIUM | messageType 214 from real cabinet |
| `burst_room_join.bin` | MEDIUM | messageType 216 from real cabinet |
| `game_data_save_request.json` | MEDIUM | HTTP POST to `/game_data/save` |
| `game_data_load_response.json` | MEDIUM | HTTP response from `/game_data/load` |
| `player_login_request.json` | LOW | HTTP POST to `/player/login` |
| `player_login_response.json` | LOW | HTTP response from `/player/login` |
| `version_request.json` | LOW | HTTP POST to `/version` |
| `version_response.json` | LOW | HTTP response from `/version` |

## How to Capture

1. **HTTP captures**: Use mitmproxy or Nginx access log with request body
2. **TCP captures**: Use `tcpdump` or Wireshark on port 6666
3. **Protobuf decode**: Use `protoc --decode` with `starwingMessage.proto`

## Fixture Format

Each capture file should be a standalone file that can be loaded by tests:
- `.json` files for HTTP request/response bodies
- `.bin` files for raw TCP wire data (4-byte length prefix + protobuf payload)
- `.txt` files for human-readable protocol notes
