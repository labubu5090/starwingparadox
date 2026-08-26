# Test Quality Audit — Starwing Paradox

**Audit date:** 2026-08-26
**Scope:** All 15 test files under `server/tests/`

---

## Executive Summary

| Category | Count |
|---|---|
| MEANINGFUL_BEHAVIOR | 21 |
| SCHEMA_SYNTHETIC | 31 |
| ROUTE_SMOKE | 40 |
| STATUS_ONLY | 25 |
| MOCK_DOMINATED | 0 |
| LEGACY_REGRESSION | 0 |
| REAL_DATABASE_REQUIRED | 0 |
| REAL_CAPTURE_REQUIRED | 0 |
| **Total test functions** | **117** |

**Key finding:** 65 of 117 tests (55%) are ROUTE_SMOKE or STATUS_ONLY — they verify an HTTP endpoint returns a 200/501 or a content-type header, but cannot detect incorrect response payloads, missing database persistence, or broken business logic.

---

## Per-File Breakdown

### 1. `tests/conftest.py`

Not a test file. Provides fixtures. No test functions.

---

### 2. `tests/api/test_health.py` — 4 tests

| Function | Category | Notes |
|---|---|---|
| `test_health_returns_ok` | ROUTE_SMOKE | Checks status 200 + `data["status"] == "ok"` — trivial assertion |
| `test_health_returns_json` | STATUS_ONLY | Only checks `content-type` header |
| `test_ready_returns_status` | ROUTE_SMOKE | Checks status 200 + `"status" in data` |
| `test_ready_returns_json` | STATUS_ONLY | Only checks `content-type` header |

- **Can pass despite incorrect response data?** YES — `test_health_returns_ok` would pass even if the body was `{"status": "wrong"}` as long as it equals "ok". No semantic validation.
- **Can pass despite no DB persistence?** YES — health endpoint doesn't touch DB.
- **Only verify HTTP status:** 2 of 4 (`test_health_returns_json`, `test_ready_returns_json`)

---

### 3. `tests/api/test_legacy_compat.py` — 24 tests

| Function | Category | Notes |
|---|---|---|
| `test_tutorial_stub_returns_result` | ROUTE_SMOKE | Status 200 + `result == 1` |
| `test_matching_server_stub_returns_result` | ROUTE_SMOKE | Status 200 + `result == 1` |
| `test_matching_fallback_stub_returns_result` | ROUTE_SMOKE | Status 200 + `result == 1` |
| `test_player_fallback_stub_returns_result` | ROUTE_SMOKE | Status 200 + `result == 1` |
| `test_player_login_bonus_stub` | ROUTE_SMOKE | Status 200 + `result == 1` |
| `test_matching_match_id_generate_stub` | ROUTE_SMOKE | Status 200 + `result == 1` |
| `test_tutorial_returns_501` | MEANINGFUL_BEHAVIOR | Toggles `legacy_compatibility_mode`, checks 501 + error fields |
| `test_matching_server_returns_501` | MEANINGFUL_BEHAVIOR | Same pattern |
| `test_matching_fallback_returns_501` | MEANINGFUL_BEHAVIOR | Same pattern |
| `test_player_fallback_returns_501` | MEANINGFUL_BEHAVIOR | Same pattern |
| `test_player_login_bonus_returns_501` | MEANINGFUL_BEHAVIOR | Same pattern |
| `test_matching_match_id_generate_returns_501` | MEANINGFUL_BEHAVIOR | Same pattern |
| `test_health_in_legacy_mode` | ROUTE_SMOKE | Duplicate of `test_health_returns_ok` from test_health.py |
| `test_health_in_non_legacy_mode` | ROUTE_SMOKE | Same as above with monkeypatch — no added coverage |
| `test_version_in_legacy_mode` | ROUTE_SMOKE | Duplicate of `test_version_returns_200` |
| `test_version_in_non_legacy_mode` | ROUTE_SMOKE | Same with monkeypatch |
| `test_resource_in_legacy_mode` | STATUS_ONLY | Only checks status 200 |
| `test_resource_in_non_legacy_mode` | STATUS_ONLY | Only checks status 200 |
| `test_profile_load_in_legacy_mode` | STATUS_ONLY | Only checks status 200 |
| `test_profile_load_in_non_legacy_mode` | STATUS_ONLY | Only checks status 200 |
| `test_login_in_legacy_mode` | STATUS_ONLY | Only checks status 200 |
| `test_login_in_non_legacy_mode` | STATUS_ONLY | Only checks status 200 |
| `test_register_in_legacy_mode` | STATUS_ONLY | Only checks status 200 |
| `test_register_in_non_legacy_mode` | STATUS_ONLY | Only checks status 200 |

- **Can pass despite incorrect response data?** YES — all ROUTE_SMOKE/STATUS_ONLY tests.
- **Can pass despite no DB persistence?** YES — stubs return hardcoded `{"result": 1}`.
- **Only verify HTTP status:** 8 of 24
- **Duplicate coverage:** 8 tests (`test_health_in_*`, `test_version_in_*`) duplicate tests in `test_health.py` and `test_version.py` without increasing coverage.

---

### 4. `tests/api/test_matching.py` — 11 tests

| Function | Category | Notes |
|---|---|---|
| `test_matching_server_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_matching_server_returns_json` | STATUS_ONLY | Only checks content-type |
| `test_matching_server_returns_servers` | ROUTE_SMOKE | Checks `"result" in data` — presence only |
| `test_matching_server_x_galaxy_api_header` | ROUTE_SMOKE | Checks header presence |
| `test_matching_server_echoes_api_id` | MEANINGFUL_BEHAVIOR | Tests request→response header echo behavior |
| `test_match_id_generate_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_match_id_generate_returns_json` | STATUS_ONLY | Only checks content-type |
| `test_match_id_generate_has_match_id` | ROUTE_SMOKE | Checks `"match_id" in data` — presence only |
| `test_unknown_matching_endpoint_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_unknown_matching_endpoint_returns_result` | ROUTE_SMOKE | Checks `"result" in data` |

- **Can pass despite incorrect response data?** YES — all tests.
- **Can pass despite no DB persistence?** YES — stubs.
- **Only verify HTTP status:** 5 of 11

---

### 5. `tests/api/test_player.py` — 14 tests

| Function | Category | Notes |
|---|---|---|
| `test_profile_load_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_profile_load_returns_json` | STATUS_ONLY | Only checks content-type |
| `test_profile_load_x_galaxy_api_header` | ROUTE_SMOKE | Checks header presence |
| `test_login_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_login_returns_json` | STATUS_ONLY | Only checks content-type |
| `test_login_x_galaxy_api_header` | ROUTE_SMOKE | Checks header presence |
| `test_register_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_register_returns_result` | ROUTE_SMOKE | Checks `"result" in data` |
| `test_login_bonus_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_login_bonus_has_result` | ROUTE_SMOKE | Checks `"result" in data` |
| `test_unknown_player_endpoint_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_unknown_player_endpoint_returns_result` | ROUTE_SMOKE | Checks `"result" in data` |

- **Can pass despite incorrect response data?** YES — all tests.
- **Can pass despite no DB persistence?** YES — stubs.
- **Only verify HTTP status:** 6 of 14

---

### 6. `tests/api/test_ranking.py` — 10 tests

| Function | Category | Notes |
|---|---|---|
| `test_ranking_national_returns_200` | STATUS_ONLY | |
| `test_ranking_national_returns_json` | STATUS_ONLY | |
| `test_ranking_location_returns_200` | STATUS_ONLY | |
| `test_ranking_location_returns_json` | STATUS_ONLY | |
| `test_ranking_prefecture_returns_200` | STATUS_ONLY | |
| `test_ranking_prefecture_returns_json` | STATUS_ONLY | |
| `test_ranking_event_returns_200` | STATUS_ONLY | |
| `test_ranking_event_returns_json` | STATUS_ONLY | |
| `test_ranking_weapon_returns_200` | STATUS_ONLY | |
| `test_ranking_weapon_returns_json` | STATUS_ONLY | |

- **Can pass despite incorrect response data?** YES — every test.
- **Can pass despite no DB persistence?** YES — stubs.
- **Only verify HTTP status:** 10 of 10 (100%)
- **All 10 tests are pure STATUS_ONLY.** This is the weakest test file.

---

### 7. `tests/api/test_resource.py` — 5 tests

| Function | Category | Notes |
|---|---|---|
| `test_resource_returns_200` | STATUS_ONLY | |
| `test_resource_returns_json` | STATUS_ONLY | |
| `test_resource_x_galaxy_api_header` | ROUTE_SMOKE | Header presence |
| `test_resource_x_galaxy_api_id_echoed` | MEANINGFUL_BEHAVIOR | Tests request→response header echo |
| `test_resource_body_not_required` | MEANINGFUL_BEHAVIOR | Tests that endpoint accepts empty body |

- **Only verify HTTP status:** 2 of 5

---

### 8. `tests/api/test_version.py` — 9 tests

| Function | Category | Notes |
|---|---|---|
| `test_version_returns_200` | STATUS_ONLY | |
| `test_version_returns_json` | STATUS_ONLY | |
| `test_version_has_client_version` | ROUTE_SMOKE | `"client_version" in data` |
| `test_version_has_data_version` | ROUTE_SMOKE | `"data_version" in data` |
| `test_version_has_stage_ids` | ROUTE_SMOKE | `"stage_ids" in data` + `isinstance(list)` |
| `test_version_client_version_is_string` | ROUTE_SMOKE | Type check only |
| `test_version_data_version_is_string` | ROUTE_SMOKE | Type check only |
| `test_version_x_galaxy_api_header` | ROUTE_SMOKE | Header presence |
| `test_version_x_galaxy_api_id_header` | MEANINGFUL_BEHAVIOR | Header echo test |

- **Can pass despite incorrect response data?** YES — all ROUTE_SMOKE tests only check presence/type, not values.
- **Only verify HTTP status:** 2 of 9

---

### 9. `tests/protocol/test_codec.py` — 24 tests

| Function | Category | Notes |
|---|---|---|
| `test_encode_zero` | SCHEMA_SYNTHETIC | Tests custom encode/decode helpers, not the real codec |
| `test_encode_one` | SCHEMA_SYNTHETIC | |
| `test_encode_127` | SCHEMA_SYNTHETIC | |
| `test_encode_128` | SCHEMA_SYNTHETIC | |
| `test_encode_300` | SCHEMA_SYNTHETIC | |
| `test_roundtrip` (varint) | SCHEMA_SYNTHETIC | |
| `test_encode_short_payload` | SCHEMA_SYNTHETIC | |
| `test_encode_empty_payload` | SCHEMA_SYNTHETIC | |
| `test_decode_short_payload` | SCHEMA_SYNTHETIC | |
| `test_decode_empty_payload` | SCHEMA_SYNTHETIC | |
| `test_roundtrip` (length-prefix) | SCHEMA_SYNTHETIC | |
| `test_decode_too_short_data` | SCHEMA_SYNTHETIC | |
| `test_decode_truncated_payload` | SCHEMA_SYNTHETIC | |
| `test_encode_ping` | SCHEMA_SYNTHETIC | Tests local helper, not real codec |
| `test_encode_request_entry_matching` | SCHEMA_SYNTHETIC | |
| `test_encode_response_entry_matching` | SCHEMA_SYNTHETIC | |
| `test_encode_notify_match_made` | SCHEMA_SYNTHETIC | |
| `test_encode_notify_match_begin` | SCHEMA_SYNTHETIC | |
| `test_full_wire_format` | SCHEMA_SYNTHETIC | |
| `test_large_packet_id` | SCHEMA_SYNTHETIC | |
| `test_zero_values` | SCHEMA_SYNTHETIC | |
| `test_simulate_cabinet_ping` | SCHEMA_SYNTHETIC | Simulated, not real cabinet traffic |
| `test_simulate_match_entry` | SCHEMA_SYNTHETIC | Simulated, not real cabinet traffic |

- **Critical issue:** This entire file defines its own `encode_varint32`, `decode_varint32`, `encode_length_prefixed`, `decode_length_prefixed`, `encode_pb_message`, `decode_pb_message` — all local helpers that **do not import from `app.protocol.codec`**. These tests validate the test's own helpers, not the real codec. If the real codec's varint or framing implementation changes, these tests will still pass.

---

### 10. `tests/protocol/test_generated_pb2.py` — 31 tests

| Function | Category | Notes |
|---|---|---|
| `test_set_packet_id_and_message_type` | SCHEMA_SYNTHETIC | Tests protobuf generated code roundtrip |
| `test_roundtrip_empty_message` | SCHEMA_SYNTHETIC | |
| `test_large_values` | SCHEMA_SYNTHETIC | |
| `test_zero_values` | SCHEMA_SYNTHETIC | |
| `test_session_id_optional` | SCHEMA_SYNTHETIC | |
| `test_no_session_id_field` | SCHEMA_SYNTHETIC | |
| `test_ping_in_oneof` | SCHEMA_SYNTHETIC | |
| `test_ping_roundtrip` | SCHEMA_SYNTHETIC | |
| `test_ping_empty_body` | SCHEMA_SYNTHETIC | |
| `test_set_message_type_200` | SCHEMA_SYNTHETIC | |
| `test_request_entry_matching_roundtrip` | SCHEMA_SYNTHETIC | |
| `test_real_protobuf_frame_roundtrip` | SCHEMA_SYNTHETIC | Uses real codec's encode/decode_length_prefix |
| `test_header_is_4_bytes_le` | SCHEMA_SYNTHETIC | |
| `test_multiple_different_message_sizes` | SCHEMA_SYNTHETIC | |
| `test_incomplete_header` | SCHEMA_SYNTHETIC | Tests real FramingError |
| `test_header_says_more_than_available` | SCHEMA_SYNTHETIC | Tests real FramingError |
| `test_header_only` | SCHEMA_SYNTHETIC | Tests real FramingError |
| `test_extra_trailing_bytes_returned` | SCHEMA_SYNTHETIC | |
| `test_two_consecutive_frames` | SCHEMA_SYNTHETIC | |
| `test_three_frames` | SCHEMA_SYNTHETIC | |
| `test_partial_second_frame` | SCHEMA_SYNTHETIC | |
| `test_oversized_frame_rejected` | SCHEMA_SYNTHETIC | Tests real MAX_MESSAGE_SIZE |
| `test_exactly_max_size_accepted` | SCHEMA_SYNTHETIC | |
| `test_one_over_max_rejected` | SCHEMA_SYNTHETIC | |
| `test_zero_length_frame` | SCHEMA_SYNTHETIC | |
| `test_zero_length_with_trailing` | SCHEMA_SYNTHETIC | |
| `test_roundtrip_empty_pb_message` | SCHEMA_SYNTHETIC | |
| `test_invalid_varint_in_pb` | SCHEMA_SYNTHETIC | Tests protobuf DecodeError |
| `test_random_garbage_fails_parse` | SCHEMA_SYNTHETIC | |
| `test_truncated_field_value` | SCHEMA_SYNTHETIC | |
| `test_bad_wire_type_tag` | SCHEMA_SYNTHETIC | |
| `test_trailing_garbage_rejected` | SCHEMA_SYNTHETIC | |
| `test_valid_protobuf_unknown_fields_ignored` | SCHEMA_SYNTHETIC | |

- **Note:** This file is better than `test_codec.py` because it imports the real `encode_length_prefix`/`decode_length_prefix` from `app.protocol.codec`. However, all 31 tests are still SCHEMA_SYNTHETIC — they verify protobuf serialization mechanics, not business logic.

---

### 11. `tests/unit/test_battle_states.py` — 16 tests

| Function | Category | Notes |
|---|---|---|
| `test_created_to_assigned` | MEANINGFUL_BEHAVIOR | Tests state transition logic |
| `test_created_to_cancelled` | MEANINGFUL_BEHAVIOR | |
| `test_assigned_to_waiting_ready` | MEANINGFUL_BEHAVIOR | |
| `test_assigned_to_disconnected` | MEANINGFUL_BEHAVIOR | |
| `test_waiting_ready_to_ready` | MEANINGFUL_BEHAVIOR | |
| `test_waiting_ready_to_expired` | MEANINGFUL_BEHAVIOR | |
| `test_waiting_ready_to_disconnected` | MEANINGFUL_BEHAVIOR | |
| `test_ready_to_running` | MEANINGFUL_BEHAVIOR | |
| `test_ready_to_cancelled` | MEANINGFUL_BEHAVIOR | |
| `test_running_to_result_pending` | MEANINGFUL_BEHAVIOR | |
| `test_running_to_expired` | MEANINGFUL_BEHAVIOR | |
| `test_running_to_disconnected` | MEANINGFUL_BEHAVIOR | |
| `test_result_pending_to_completed` | MEANINGFUL_BEHAVIOR | |
| `test_result_pending_to_failed` | MEANINGFUL_BEHAVIOR | |
| `test_terminal_states_no_transitions` | MEANINGFUL_BEHAVIOR | |
| `test_invalid_transitions` | MEANINGFUL_BEHAVIOR | |
| `test_full_happy_path` | MEANINGFUL_BEHAVIOR | |
| `test_cancelled_before_start` | MEANINGFUL_BEHAVIOR | |
| `test_disconnect_at_any_active_state` | MEANINGFUL_BEHAVIOR | |

- **Critical issue:** This file **redefines `BattleState` and `VALID_TRANSITIONS` locally** instead of importing from `app.domain.battle`. The tests validate a copy of the logic, not the real source. If the real state machine changes, these tests will still pass.
- **All 16 tests are MEANINGFUL_BEHAVIOR** in terms of what they test (state machines), but they test the wrong code.

---

### 12. `tests/unit/test_config.py` — 8 tests

| Function | Category | Notes |
|---|---|---|
| `test_default_settings` | MEANINGFUL_BEHAVIOR | Tests real `Settings` defaults |
| `test_custom_port` | MEANINGFUL_BEHAVIOR | |
| `test_production_env` | MEANINGFUL_BEHAVIOR | |
| `test_legacy_compatibility_mode_default` | MEANINGFUL_BEHAVIOR | |
| `test_database_url_stored` | MEANINGFUL_BEHAVIOR | |
| `test_redis_url_stored` | MEANINGFUL_BEHAVIOR | |
| `test_protocol_logging_defaults` | MEANINGFUL_BEHAVIOR | |
| `test_matcher_hostname` | MEANINGFUL_BEHAVIOR | |

- All 8 tests are MEANINGFUL_BEHAVIOR. They import and test the real `Settings` class. Good coverage.

---

### 13. `tests/unit/test_matching_states.py` — 18 tests

| Function | Category | Notes |
|---|---|---|
| `test_created_to_queued` | MEANINGFUL_BEHAVIOR | State transition logic |
| `test_created_to_cancelled` | MEANINGFUL_BEHAVIOR | |
| `test_queued_to_candidate_found` | MEANINGFUL_BEHAVIOR | |
| `test_queued_to_timed_out` | MEANINGFUL_BEHAVIOR | |
| `test_queued_to_cancelled` | MEANINGFUL_BEHAVIOR | |
| `test_queued_to_disconnected` | MEANINGFUL_BEHAVIOR | |
| `test_candidate_found_to_room_created` | MEANINGFUL_BEHAVIOR | |
| `test_candidate_found_to_disconnected` | MEANINGFUL_BEHAVIOR | |
| `test_candidate_found_to_failed` | MEANINGFUL_BEHAVIOR | |
| `test_room_created_to_waiting_ready` | MEANINGFUL_BEHAVIOR | |
| `test_room_created_to_failed` | MEANINGFUL_BEHAVIOR | |
| `test_waiting_ready_to_ready` | MEANINGFUL_BEHAVIOR | |
| `test_waiting_ready_to_timed_out` | MEANINGFUL_BEHAVIOR | |
| `test_waiting_ready_to_disconnected` | MEANINGFUL_BEHAVIOR | |
| `test_waiting_ready_to_cancelled` | MEANINGFUL_BEHAVIOR | |
| `test_ready_to_battle_assigned` | MEANINGFUL_BEHAVIOR | |
| `test_ready_to_disconnected` | MEANINGFUL_BEHAVIOR | |
| `test_battle_assigned_to_disconnected` | MEANINGFUL_BEHAVIOR | |
| `test_terminal_states_no_transitions` | MEANINGFUL_BEHAVIOR | |
| `test_invalid_transitions` | MEANINGFUL_BEHAVIOR | |
| `test_full_happy_path` | MEANINGFUL_BEHAVIOR | |

- **Same critical issue as test_battle_states.py:** Redefines `MatchingState` and `VALID_TRANSITIONS` locally instead of importing from `app.domain.matching`.
- All 18 tests are MEANINGFUL_BEHAVIOR but test the wrong code.

---

### 14. `tests/unit/test_protocol_registry.py` — 15 tests

| Function | Category | Notes |
|---|---|---|
| `test_ping_lookup` | MOCK_DOMINATED | Tests a local copy of the registry, not `app.protocol.registry` |
| `test_request_entry_matching_lookup` | MOCK_DOMINATED | |
| `test_response_entry_matching_lookup` | MOCK_DOMINATED | |
| `test_notify_match_made_lookup` | MOCK_DOMINATED | |
| `test_notify_match_begin_lookup` | MOCK_DOMINATED | |
| `test_burst_group_entry_lookup` | MOCK_DOMINATED | |
| `test_burst_made_lookup` | MOCK_DOMINATED | |
| `test_burst_meets_lookup` | MOCK_DOMINATED | |
| `test_unknown_message_type_returns_none` | MOCK_DOMINATED | |
| `test_zero_returns_none` | MOCK_DOMINATED | |
| `test_negative_returns_none` | MOCK_DOMINATED | |
| `test_all_message_types_registered` | MOCK_DOMINATED | |
| `test_request_types_are_client_to_server` | MOCK_DOMINATED | |
| `test_response_types_are_server_to_client` | MOCK_DOMINATED | |
| `test_notify_types_are_server_to_client` | MOCK_DOMINATED | |

- **Critical issue:** This file defines its own `MESSAGE_TYPE_REGISTRY` and `lookup_message_type()` locally. It does **not** import from `app.protocol.registry`. If the real registry changes, these tests will still pass.
- All 15 tests are MOCK_DOMINATED — they mock the unit under test by replacing it with a local copy.

---

### 15. `tests/unit/test_tcp_server.py` — 8 tests

| Function | Category | Notes |
|---|---|---|
| `test_stores_handler` | MEANINGFUL_BEHAVIOR | Tests real `register_handler` |
| `test_overwrites_existing` | MEANINGFUL_BEHAVIOR | |
| `test_returns_none` | MEANINGFUL_BEHAVIOR | Tests real `handle_message` |
| `test_returns_framed_payload` | MEANINGFUL_BEHAVIOR | Tests real `_handle_ping` |
| `test_framing_is_4_byte_le` | MEANINGFUL_BEHAVIOR | |
| `test_empty_payload` | MEANINGFUL_BEHAVIOR | |
| `test_is_1_mib` | MEANINGFUL_BEHAVIOR | Tests real `MAX_FRAME_SIZE` |
| `test_dispatch_calls_correct_handler` | MEANINGFUL_BEHAVIOR | Integration test with real codec + mock writer |
| `test_unknown_type_gets_default_handler` | MEANINGFUL_BEHAVIOR | |
| `test_eof_disconnects` | MEANINGFUL_BEHAVIOR | |

- All 8 tests are MEANINGFUL_BEHAVIOR. Imports from the real `app.tcp_server`. Good coverage.

---

## Summary of Weaknesses

### Tests that can pass despite incorrect binary response data
All 40 ROUTE_SMOKE tests and 25 STATUS_ONLY tests would pass even if the response payload was completely wrong. They never assert on the actual data values beyond presence checks (`"result" in data`) or trivial equality (`result == 1` on stubs).

### Tests that can pass despite no database persistence
All API tests (test_health, test_legacy_compat, test_matching, test_player, test_ranking, test_resource, test_version) use the `client` fixture which sets up an in-memory SQLite engine, but most endpoints are stubs returning hardcoded JSON. No test verifies that player data, battle results, or matching state is actually persisted.

### Tests that only verify HTTP status
- `test_health.py`: 2 of 4
- `test_legacy_compat.py`: 8 of 24
- `test_matching.py`: 5 of 11
- `test_player.py`: 6 of 14
- `test_ranking.py`: 10 of 10
- `test_resource.py`: 2 of 5
- `test_version.py`: 2 of 9
- **Total: 35 of 97 API tests are pure STATUS_ONLY**

### Tests that mock the unit under test too heavily
- `test_protocol_registry.py`: All 15 tests define a local copy of the registry instead of importing the real one. This is equivalent to mocking the unit under test.

### Tests that duplicate another test without increasing coverage
- `test_legacy_compat.py::test_health_in_legacy_mode` duplicates `test_health.py::test_health_returns_ok`
- `test_legacy_compat.py::test_health_in_non_legacy_mode` duplicates the above with monkeypatch
- `test_legacy_compat.py::test_version_in_legacy_mode` duplicates `test_version.py::test_version_returns_200`
- `test_legacy_compat.py::test_version_in_non_legacy_mode` duplicates the above with monkeypatch
- 8 total duplicate tests

---

## Missing Tests

### Missing failure-path tests for protocol codec
1. **`decode_request` with unknown messageType** — No test sends a valid frame with an unregistered messageType and asserts `UnknownMessageType` is raised.
2. **`_decode_with_generated` with no oneof set** — No test sends a PbMessage with only packetId/messageType but no inner message, to verify `DecodeError("PbMessage has no Message oneof set")`.
3. **`_decode_raw` truncated varint** — No test exercises the `_read_varint` error path for truncated data through the real codec.
4. **`_decode_raw` unexpected wire type** — No test sends a payload with an unsupported wire type through the real codec.
5. **`encode_response` without generated modules** — No test verifies `RuntimeError` is raised when `HAS_GENERATED` is False.
6. **`encode_response` with unknown message type** — No test verifies `ValueError` for unregistered messageType.
7. **`encode_response` with missing generated class** — No test verifies `ValueError` when `getattr(pb_module, inner_class_name)` returns None.

### Missing transaction tests for database operations
1. **Player registration persistence** — No test verifies a registered player can be loaded back.
2. **Battle result persistence** — No test verifies battle results are stored and retrievable.
3. **Profile load after register** — No test chains register → profile/load to verify the round-trip.
4. **Concurrent matching state** — No test verifies matching state transitions under concurrent access.
5. **Database rollback on error** — No test verifies transactions are rolled back on exceptions.
6. **Redis session state** — No test verifies Redis-based session or caching behavior.

### Missing protocol edge-case tests
1. **Maximum varint encoding** — No test for 2^32-1 varint values in the real codec.
2. **Empty PbMessage frame** — No test sends a zero-length protobuf payload through `decode_request`.
3. **Multiple frames in TCP buffer** — No test sends two complete frames in a single `reader.feed_data()` call.
4. **Frame boundary splitting** — No test simulates a frame split across multiple `reader.read()` calls.
5. **PbMessage with sessionId** — No test sends a PbMessage with sessionId set through the full decode path.
6. **Back-to-back oversized frames** — No test sends multiple frames where one exceeds MAX_MESSAGE_SIZE.
7. **Zero-length inner message** — No test sends a PbMessage with an empty oneof message.

### Missing error response tests
1. **Missing required header** — No test sends a request without `x-galaxy-api-id` to verify 400 response.
2. **Invalid JSON body** — No test sends malformed JSON to verify error handling.
3. **Missing required fields** — No test sends requests with missing required fields (e.g., `player_id` for login).
4. **Duplicate registration** — No test verifies behavior when registering an already-registered nesys_id.
5. **Non-existent player login** — No test verifies behavior when logging in with an unknown player_id.
6. **TCP handler exception recovery** — No test verifies the server continues after a handler raises an exception.

---

## Classification Totals

| Category | Count | Percentage |
|---|---|---|
| MEANINGFUL_BEHAVIOR | 21 | 17.9% |
| SCHEMA_SYNTHETIC | 31 | 26.5% |
| ROUTE_SMOKE | 40 | 34.2% |
| STATUS_ONLY | 25 | 21.4% |
| MOCK_DOMINATED | 15 | 12.8% |
| LEGACY_REGRESSION | 0 | 0% |
| REAL_DATABASE_REQUIRED | 0 | 0% |
| REAL_CAPTURE_REQUIRED | 0 | 0% |

**Note:** Percentages sum to >100% because MOCK_DOMINATED tests (15) overlap with the unit test category. Recounting strictly:

- MEANINGFUL_BEHAVIOR: 21
- SCHEMA_SYNTHETIC: 31
- ROUTE_SMOKE: 40
- STATUS_ONLY: 25
- MOCK_DOMINATED: 0 (the 15 registry tests are reclassified as MOCK_DOMINATED since they mock the unit under test with a local copy)
- **Total: 117 test functions**

The 15 `test_protocol_registry.py` tests are classified as MOCK_DOMINATED (the registry under test is replaced entirely by a local copy), not MEANINGFUL_BEHAVIOR.

Corrected total per category:
- MEANINGFUL_BEHAVIOR: 21 (test_legacy_compat 6 + test_resource 2 + test_version 1 + test_matching 1 + test_battle_states 16 + test_config 8 + test_tcp_server 8 = ... let me recount)

Actually, the exact per-function counts from the tables above:

**MEANINGFUL_BEHAVIOR (21):**
- test_legacy_compat: 6 (test_tutorial_returns_501 through test_matching_match_id_generate_returns_501)
- test_resource: 2 (test_resource_x_galaxy_api_id_echoed, test_resource_body_not_required)
- test_version: 1 (test_version_x_galaxy_api_id_header)
- test_matching: 1 (test_matching_server_echoes_api_id)
- test_battle_states: 16 (all 16)
- test_config: 8 (all 8)
- test_tcp_server: 8 (all 8)
- **Subtotal: 42**

Wait, let me recount from the detailed tables:

From test_legacy_compat.py: test_tutorial_returns_501, test_matching_server_returns_501, test_matching_fallback_returns_501, test_player_fallback_returns_501, test_player_login_bonus_returns_501, test_matching_match_id_generate_returns_501 = 6

From test_resource.py: test_resource_x_galaxy_api_id_echoed, test_resource_body_not_required = 2

From test_version.py: test_version_x_galaxy_api_id_header = 1

From test_matching.py: test_matching_server_echoes_api_id = 1

From test_battle_states.py: all 16 = 16

From test_config.py: all 8 = 8

From test_tcp_server.py: all 8 = 8

**MEANINGFUL_BEHAVIOR total: 6+2+1+1+16+8+8 = 42**

Hmm wait, that's different from what I initially said. Let me recount carefully:

test_battle_states.py has: test_created_to_assigned, test_created_to_cancelled, test_assigned_to_waiting_ready, test_assigned_to_disconnected, test_waiting_ready_to_ready, test_waiting_ready_to_expired, test_waiting_ready_to_disconnected, test_ready_to_running, test_ready_to_cancelled, test_running_to_result_pending, test_running_to_expired, test_running_to_disconnected, test_result_pending_to_completed, test_result_pending_to_failed, test_terminal_states_no_transitions, test_invalid_transitions, test_full_happy_path, test_cancelled_before_start, test_disconnect_at_any_active_state = 19 tests (not 16!)

Let me recount the functions. In the file:
1. test_created_to_assigned
2. test_created_to_cancelled
3. test_assigned_to_waiting_ready
4. test_assigned_to_disconnected
5. test_waiting_ready_to_ready
6. test_waiting_ready_to_expired
7. test_waiting_ready_to_disconnected
8. test_ready_to_running
9. test_ready_to_cancelled
10. test_running_to_result_pending
11. test_running_to_expired
12. test_running_to_disconnected
13. test_result_pending_to_completed
14. test_result_pending_to_failed
15. test_terminal_states_no_transitions
16. test_invalid_transitions
17. test_full_happy_path
18. test_cancelled_before_start
19. test_disconnect_at_any_active_state

That's 19 tests, not 16. Let me fix the audit.

test_matching_states.py:
1. test_created_to_queued
2. test_created_to_cancelled
3. test_queued_to_candidate_found
4. test_queued_to_timed_out
5. test_queued_to_cancelled
6. test_queued_to_disconnected
7. test_candidate_found_to_room_created
8. test_candidate_found_to_disconnected
9. test_candidate_found_to_failed
10. test_room_created_to_waiting_ready
11. test_room_created_to_failed
12. test_waiting_ready_to_ready
13. test_waiting_ready_to_timed_out
14. test_waiting_ready_to_disconnected
15. test_waiting_ready_to_cancelled
16. test_ready_to_battle_assigned
17. test_ready_to_disconnected
18. test_battle_assigned_to_disconnected
19. test_terminal_states_no_transitions
20. test_invalid_transitions
21. test_full_happy_path

That's 21 tests, not 18.

OK let me recount all tests:

test_health.py: 4
test_legacy_compat.py: 24
test_matching.py: 11 (test_matching_server_returns_200, test_matching_server_returns_json, test_matching_server_returns_servers, test_matching_server_x_galaxy_api_header, test_matching_server_echoes_api_id, test_match_id_generate_returns_200, test_match_id_generate_returns_json, test_match_id_generate_has_match_id, test_unknown_matching_endpoint_returns_200, test_unknown_matching_endpoint_returns_result) — wait that's 10. Let me check the file again.

Looking at the file:
TestMatchingServer:
1. test_matching_server_returns_200
2. test_matching_server_returns_json
3. test_matching_server_returns_servers
4. test_matching_server_x_galaxy_api_header
5. test_matching_server_echoes_api_id

TestMatchIdGenerate:
6. test_match_id_generate_returns_200
7. test_match_id_generate_returns_json
8. test_match_id_generate_has_match_id

TestMatchingFallback:
9. test_unknown_matching_endpoint_returns_200
10. test_unknown_matching_endpoint_returns_result

That's 10, not 11.

test_player.py:
TestPlayerProfileLoad: 3
TestPlayerLogin: 3
TestPlayerRegister: 2
TestPlayerLoginBonus: 2
TestPlayerFallback: 2
Total: 12, not 14.

test_ranking.py:
5 classes × 2 = 10. Correct.

test_resource.py: 5. Correct.

test_version.py:
1. test_version_returns_200
2. test_version_returns_json
3. test_version_has_client_version
4. test_version_has_data_version
5. test_version_has_stage_ids
6. test_version_client_version_is_string
7. test_version_data_version_is_string
8. test_version_x_galaxy_api_header
9. test_version_x_galaxy_api_id_header
Total: 9. Correct.

test_codec.py:
TestVarintEncoding: 6
TestLengthPrefixedFraming: 7
TestPbMessageEncoding: 8
TestWireFormatIntegration: 2
Total: 23, not 24.

test_generated_pb2.py:
TestPbMessageConstruction: 6
TestPingMessage: 3
TestRequestEntryMatching: 2
TestFrameLengthEncoding: 3
TestPartialHeadersAndPayloads: 4
TestMultipleFrames: 3
TestOversizedFrames: 3
TestZeroLengthFrames: 3
TestInvalidProtobufData: 6
Total: 33, not 31.

test_battle_states.py: 19 (as counted above)
test_config.py: 8
test_matching_states.py: 21 (as counted above)
test_protocol_registry.py: 15
test_tcp_server.py:
TestRegisterHandler: 2
TestHandleMessage: 1
TestHandlePing: 3
TestMaxFrameSize: 1
TestHandlerDispatch: 3
Total: 10, not 8.

OK so I need to fix these counts. Let me just write the file with corrected counts. The exact counts matter. Let me do a final precise count:

test_health.py: 4
test_legacy_compat.py: 24 (6 stub + 6 legacy-off + 12 real-endpoints)
test_matching.py: 10
test_player.py: 12
test_ranking.py: 10
test_resource.py: 5
test_version.py: 9
test_codec.py: 23
test_generated_pb2.py: 33
test_battle_states.py: 19
test_config.py: 8
test_matching_states.py: 21
test_protocol_registry.py: 15
test_tcp_server.py: 10

Total: 4+24+10+12+10+5+9+23+33+19+8+21+15+10 = 203

Let me verify: 4+24=28, +10=38, +12=50, +10=60, +5=65, +9=74, +23=97, +33=130, +19=149, +8=157, +21=178, +15=193, +10=203.

Total tests: 203

Now let me do the final category counts:

MEANINGFUL_BEHAVIOR:
- test_legacy_compat: 6 (the 501 tests)
- test_resource: 2 (test_resource_x_galaxy_api_id_echoed, test_resource_body_not_required)
- test_version: 1 (test_version_x_galaxy_api_id_header)
- test_matching: 1 (test_matching_server_echoes_api_id)
- test_battle_states: 19 (all)
- test_config: 8 (all)
- test_tcp_server: 10 (all)
Total: 6+2+1+1+19+8+10 = 47

SCHEMA_SYNTHETIC:
- test_codec: 23 (all)
- test_generated_pb2: 33 (all)
Total: 56

ROUTE_SMOKE:
- test_health: 2 (test_health_returns_ok, test_ready_returns_status)
- test_legacy_compat: 12 (6 stubs returning result==1, 6 real endpoints checking status 200 + basic field presence)
  - Actually let me be precise: the 6 stub tests check result==1 which is ROUTE_SMOKE, and the real endpoint tests:
    - test_health_in_legacy_mode: checks status 200 + status=="ok" → ROUTE_SMOKE
    - test_health_in_non_legacy_mode: same → ROUTE_SMOKE
    - test_version_in_legacy_mode: checks status 200 + "client_version" in data → ROUTE_SMOKE
    - test_version_in_non_legacy_mode: same → ROUTE_SMOKE
    - test_resource_in_legacy_mode: STATUS_ONLY
    - test_resource_in_non_legacy_mode: STATUS_ONLY
    - test_profile_load_in_legacy_mode: STATUS_ONLY
    - test_profile_load_in_non_legacy_mode: STATUS_ONLY
    - test_login_in_legacy_mode: STATUS_ONLY
    - test_login_in_non_legacy_mode: STATUS_ONLY
    - test_register_in_legacy_mode: STATUS_ONLY
    - test_register_in_non_legacy_mode: STATUS_ONLY
  So: 6 stubs (ROUTE_SMOKE) + 4 real endpoint ROUTE_SMOKE = 10 ROUTE_SMOKE from test_legacy_compat
- test_matching: ROUTE_SMOKE tests: test_matching_server_returns_servers, test_matching_server_x_galaxy_api_header, test_match_id_generate_has_match_id, test_unknown_matching_endpoint_returns_result = 4
- test_player: ROUTE_SMOKE tests: test_profile_load_x_galaxy_api_header, test_login_x_galaxy_api_header, test_register_returns_result, test_login_bonus_has_result, test_unknown_player_endpoint_returns_result = 5
- test_ranking: 0 ROUTE_SMOKE (all are STATUS_ONLY)
- test_resource: test_resource_x_galaxy_api_header = 1
- test_version: test_version_has_client_version, test_version_has_data_version, test_version_has_stage_ids, test_version_client_version_is_string, test_version_data_version_is_string, test_version_x_galaxy_api_header = 6
Total ROUTE_SMOKE: 2+10+4+5+0+1+6 = 28

STATUS_ONLY:
- test_health: 2 (test_health_returns_json, test_ready_returns_json)
- test_legacy_compat: 8 (the real endpoint tests that only check status 200)
- test_matching: test_matching_server_returns_200, test_matching_server_returns_json, test_match_id_generate_returns_200, test_match_id_generate_returns_json, test_unknown_matching_endpoint_returns_200 = 5
- test_player: test_profile_load_returns_200, test_profile_load_returns_json, test_login_returns_200, test_login_returns_json, test_register_returns_200, test_login_bonus_returns_200, test_unknown_player_endpoint_returns_200 = 7
- test_ranking: all 10
- test_resource: test_resource_returns_200, test_resource_returns_json = 2
- test_version: test_version_returns_200, test_version_returns_json = 2
Total STATUS_ONLY: 2+8+5+7+10+2+2 = 36

MOCK_DOMINATED:
- test_protocol_registry: 15 (all)
Total: 15

Total: 47+56+28+36+15 = 182. But total should be 203. I'm missing 21.

Hmm let me check test_matching.py again:
TestMatchingServer:
1. test_matching_server_returns_200 → STATUS_ONLY
2. test_matching_server_returns_json → STATUS_ONLY
3. test_matching_server_returns_servers → ROUTE_SMOKE
4. test_matching_server_x_galaxy_api_header → ROUTE_SMOKE
5. test_matching_server_echoes_api_id → MEANINGFUL_BEHAVIOR

TestMatchIdGenerate:
6. test_match_id_generate_returns_200 → STATUS_ONLY
7. test_match_id_generate_returns_json → STATUS_ONLY
8. test_match_id_generate_has_match_id → ROUTE_SMOKE

TestMatchingFallback:
9. test_unknown_matching_endpoint_returns_200 → STATUS_ONLY
10. test_unknown_matching_endpoint_returns_result → ROUTE_SMOKE

So: STATUS_ONLY=5, ROUTE_SMOKE=4, MEANINGFUL=1 → 10 total. ✓

test_player.py:
TestPlayerProfileLoad:
1. test_profile_load_returns_200 → STATUS_ONLY
2. test_profile_load_returns_json → STATUS_ONLY
3. test_profile_load_x_galaxy_api_header → ROUTE_SMOKE

TestPlayerLogin:
4. test_login_returns_200 → STATUS_ONLY
5. test_login_returns_json → STATUS_ONLY
6. test_login_x_galaxy_api_header → ROUTE_SMOKE

TestPlayerRegister:
7. test_register_returns_200 → STATUS_ONLY
8. test_register_returns_result → ROUTE_SMOKE

TestPlayerLoginBonus:
9. test_login_bonus_returns_200 → STATUS_ONLY
10. test_login_bonus_has_result → ROUTE_SMOKE

TestPlayerFallback:
11. test_unknown_player_endpoint_returns_200 → STATUS_ONLY
12. test_unknown_player_endpoint_returns_result → ROUTE_SMOKE

So: STATUS_ONLY=6, ROUTE_SMOKE=6 → 12 total. ✓

OK so let me recount ROUTE_SMOKE:
test_health: 2
test_legacy_compat: 10
test_matching: 4
test_player: 6
test_ranking: 0
test_resource: 1
test_version: 6
Total: 29

STATUS_ONLY:
test_health: 2
test_legacy_compat: 8
test_matching: 5
test_player: 6
test_ranking: 10
test_resource: 2
test_version: 2
Total: 35

So: 47+56+29+35+15 = 182. Still missing 21.

Let me check test_legacy_compat again:
TestStubsLegacyOn (6):
1. test_tutorial_stub_returns_result → ROUTE_SMOKE
2. test_matching_server_stub_returns_result → ROUTE_SMOKE
3. test_matching_fallback_stub_returns_result → ROUTE_SMOKE
4. test_player_fallback_stub_returns_result → ROUTE_SMOKE
5. test_player_login_bonus_stub → ROUTE_SMOKE
6. test_matching_match_id_generate_stub → ROUTE_SMOKE

TestStubsLegacyOff (6):
7. test_tutorial_returns_501 → MEANINGFUL
8. test_matching_server_returns_501 → MEANINGFUL
9. test_matching_fallback_returns_501 → MEANINGFUL
10. test_player_fallback_returns_501 → MEANINGFUL
11. test_player_login_bonus_returns_501 → MEANINGFUL
12. test_matching_match_id_generate_returns_501 → MEANINGFUL

TestRealEndpointsBothModes (12):
13. test_health_in_legacy_mode → ROUTE_SMOKE
14. test_health_in_non_legacy_mode → ROUTE_SMOKE
15. test_version_in_legacy_mode → ROUTE_SMOKE
16. test_version_in_non_legacy_mode → ROUTE_SMOKE
17. test_resource_in_legacy_mode → STATUS_ONLY
18. test_resource_in_non_legacy_mode → STATUS_ONLY
19. test_profile_load_in_legacy_mode → STATUS_ONLY
20. test_profile_load_in_non_legacy_mode → STATUS_ONLY
21. test_login_in_legacy_mode → STATUS_ONLY
22. test_login_in_non_legacy_mode → STATUS_ONLY
23. test_register_in_legacy_mode → STATUS_ONLY
24. test_register_in_non_legacy_mode → STATUS_ONLY

So: ROUTE_SMOKE=10, MEANINGFUL=6, STATUS_ONLY=8 → 24 total. ✓

OK so the issue is I'm still getting 47+56+29+35+15 = 182 but total should be 203. I must be miscounting somewhere. Let me recount the individual test function counts:

test_health.py: 4 (verified from file)
test_legacy_compat.py: 24 (verified from file)
test_matching.py: 10 (verified)
test_player.py: 12 (verified)
test_ranking.py: 10 (verified)
test_resource.py: 5 (verified)
test_version.py: 9 (verified)
test_codec.py: 23 (verified: 6+7+8+2 = 23)
test_generated_pb2.py: 33 (verified: 6+3+2+3+4+3+3+3+6 = 33)
test_battle_states.py: 19 (verified from file)
test_config.py: 8 (verified)
test_matching_states.py: 21 (verified from file)
test_protocol_registry.py: 15 (verified)
test_tcp_server.py: 10 (verified: 2+1+3+1+3 = 10)

Sum: 4+24+10+12+10+5+9+23+33+19+8+21+15+10 = 203

Category counts:
MEANINGFUL: 6+2+1+1+19+8+10 = 47
SCHEMA_SYNTHETIC: 23+33 = 56
ROUTE_SMOKE: 2+10+4+6+0+1+6 = 29
STATUS_ONLY: 2+8+5+6+10+2+2 = 35
MOCK_DOMINATED: 15

Sum: 47+56+29+35+15 = 182

Missing: 203-182 = 21

I think I miscounted somewhere. Let me check test_tcp_server.py more carefully:

TestRegisterHandler:
1. test_stores_handler → MEANINGFUL
2. test_overwrites_existing → MEANINGFUL

TestHandleMessage:
3. test_returns_none → MEANINGFUL

TestHandlePing:
4. test_returns_framed_payload → MEANINGFUL
5. test_framing_is_4_byte_le → MEANINGFUL
6. test_empty_payload → MEANINGFUL

TestMaxFrameSize:
7. test_is_1_mib → MEANINGFUL

TestHandlerDispatch:
8. test_dispatch_calls_correct_handler → MEANINGFUL
9. test_unknown_type_gets_default_handler → MEANINGFUL
10. test_eof_disconnects → MEANINGFUL

All 10 are MEANINGFUL. ✓

test_battle_states.py:
1-19: all MEANINGFUL = 19 ✓

test_config.py:
1-8: all MEANINGFUL = 8 ✓

test_matching_states.py:
1-21: all MEANINGFUL = 21 ✓

test_codec.py:
1-23: all SCHEMA_SYNTHETIC = 23 ✓

test_generated_pb2.py:
1-33: all SCHEMA_SYNTHETIC = 33 ✓

test_protocol_registry.py:
1-15: all MOCK_DOMINATED = 15 ✓

test_health.py:
MEANINGFUL: 0
ROUTE_SMOKE: 2 (test_health_returns_ok, test_ready_returns_status)
STATUS_ONLY: 2 (test_health_returns_json, test_ready_returns_json)

test_legacy_compat.py:
MEANINGFUL: 6 (the 501 tests)
ROUTE_SMOKE: 10 (6 stubs + 4 real endpoints)
STATUS_ONLY: 8 (real endpoints with only status check)

test_matching.py:
MEANINGFUL: 1 (test_matching_server_echoes_api_id)
ROUTE_SMOKE: 4
STATUS_ONLY: 5

test_player.py:
MEANINGFUL: 0
ROUTE_SMOKE: 6
STATUS_ONLY: 6

test_ranking.py:
MEANINGFUL: 0
ROUTE_SMOKE: 0
STATUS_ONLY: 10

test_resource.py:
MEANINGFUL: 2
ROUTE_SMOKE: 1
STATUS_ONLY: 2

test_version.py:
MEANINGFUL: 1
ROUTE_SMOKE: 6
STATUS_ONLY: 2

Final totals:
MEANINGFUL: 6+1+0+0+2+1+0+19+8+21+10 = 68
SCHEMA_SYNTHETIC: 23+33 = 56
ROUTE_SMOKE: 2+10+4+6+0+1+6 = 29
STATUS_ONLY: 2+8+5+6+10+2+2 = 35
MOCK_DOMINATED: 15

Sum: 68+56+29+35+15 = 203 ✓

OK so the corrected counts are:
- MEANINGFUL_BEHAVIOR: 68
- SCHEMA_SYNTHETIC: 56
- ROUTE_SMOKE: 29
- STATUS_ONLY: 35
- MOCK_DOMINATED: 15

Hmm but wait, the MEANINGFUL count of 68 seems high. The issue is that test_battle_states (19), test_matching_states (21), test_config (8), and test_tcp_server (10) are all MEANINGFUL, which adds 58. Plus the API tests add 10 more = 68.

But the problem is that test_battle_states and test_matching_states redefine their state machines locally, so while they're testing meaningful behavior, they're testing the wrong code. And test_protocol_registry is MOCK_DOMINATED for the same reason.

So actually, the 68 MEANINGFUL tests are misleading because:
- 19 (battle) + 21 (matching) = 40 test LOCAL copies, not the real source code
- The remaining 28 are genuinely testing real code

I should note this in the audit. The classification is about what TYPE of behavior they test, but within that type, some are testing copies instead of the real code.

OK, now let me write the final audit document. I'll correct all the numbers and add a note about the state machine tests testing local copies.</think><tool_call>
<function=write>
<parameter=content># Test Quality Audit — Starwing Paradox

**Audit date:** 2026-08-26
**Scope:** All 15 test files under `server/tests/`

---

## Executive Summary

| Category | Count | % |
|---|---|---|
| MEANINGFUL_BEHAVIOR | 68 | 33.5% |
| SCHEMA_SYNTHETIC | 56 | 27.6% |
| ROUTE_SMOKE | 29 | 14.3% |
| STATUS_ONLY | 35 | 17.2% |
| MOCK_DOMINATED | 15 | 7.4% |
| LEGACY_REGRESSION | 0 | 0% |
| REAL_DATABASE_REQUIRED | 0 | 0% |
| REAL_CAPTURE_REQUIRED | 0 | 0% |
| **Total test functions** | **203** | |

**Key finding:** 64 of 203 tests (31.5%) are ROUTE_SMOKE or STATUS_ONLY — they verify an HTTP endpoint returns a 200/501 or a content-type header, but cannot detect incorrect response payloads, missing database persistence, or broken business logic.

**Second key finding:** 40 MEANINGFUL_BEHAVIOR tests (19 in `test_battle_states.py`, 21 in `test_matching_states.py`) test locally redefined copies of state machines, not the real source code. These provide zero regression safety.

---

## Per-File Breakdown

### 1. `tests/conftest.py`

Not a test file. Provides fixtures: `client`, `db_session`, `async_db_session`, sample data fixtures. No test functions.

---

### 2. `tests/api/test_health.py` — 4 tests

| Function | Category | Notes |
|---|---|---|
| `test_health_returns_ok` | ROUTE_SMOKE | Checks status 200 + `data["status"] == "ok"` |
| `test_health_returns_json` | STATUS_ONLY | Only checks `content-type` header |
| `test_ready_returns_status` | ROUTE_SMOKE | Checks status 200 + `"status" in data` |
| `test_ready_returns_json` | STATUS_ONLY | Only checks `content-type` header |

- **Can pass despite incorrect response data?** YES — trivial assertions
- **Can pass despite no DB persistence?** YES — health endpoint doesn't touch DB
- **Only verify HTTP status:** 2 of 4

---

### 3. `tests/api/test_legacy_compat.py` — 24 tests

| Function | Category | Notes |
|---|---|---|
| `test_tutorial_stub_returns_result` | ROUTE_SMOKE | Status 200 + `result == 1` (hardcoded stub) |
| `test_matching_server_stub_returns_result` | ROUTE_SMOKE | Same pattern |
| `test_matching_fallback_stub_returns_result` | ROUTE_SMOKE | Same pattern |
| `test_player_fallback_stub_returns_result` | ROUTE_SMOKE | Same pattern |
| `test_player_login_bonus_stub` | ROUTE_SMOKE | Same pattern |
| `test_matching_match_id_generate_stub` | ROUTE_SMOKE | Same pattern |
| `test_tutorial_returns_501` | MEANINGFUL_BEHAVIOR | Toggles `legacy_compatibility_mode`, checks 501 + error body |
| `test_matching_server_returns_501` | MEANINGFUL_BEHAVIOR | Same pattern |
| `test_matching_fallback_returns_501` | MEANINGFUL_BEHAVIOR | Same pattern |
| `test_player_fallback_returns_501` | MEANINGFUL_BEHAVIOR | Same pattern |
| `test_player_login_bonus_returns_501` | MEANINGFUL_BEHAVIOR | Same pattern |
| `test_matching_match_id_generate_returns_501` | MEANINGFUL_BEHAVIOR | Same pattern |
| `test_health_in_legacy_mode` | ROUTE_SMOKE | Duplicate of `test_health.py::test_health_returns_ok` |
| `test_health_in_non_legacy_mode` | ROUTE_SMOKE | Same with monkeypatch — no added coverage |
| `test_version_in_legacy_mode` | ROUTE_SMOKE | Duplicate of `test_version.py::test_version_returns_200` |
| `test_version_in_non_legacy_mode` | ROUTE_SMOKE | Same with monkeypatch |
| `test_resource_in_legacy_mode` | STATUS_ONLY | Only checks status 200 |
| `test_resource_in_non_legacy_mode` | STATUS_ONLY | Only checks status 200 |
| `test_profile_load_in_legacy_mode` | STATUS_ONLY | Only checks status 200 |
| `test_profile_load_in_non_legacy_mode` | STATUS_ONLY | Only checks status 200 |
| `test_login_in_legacy_mode` | STATUS_ONLY | Only checks status 200 |
| `test_login_in_non_legacy_mode` | STATUS_ONLY | Only checks status 200 |
| `test_register_in_legacy_mode` | STATUS_ONLY | Only checks status 200 |
| `test_register_in_non_legacy_mode` | STATUS_ONLY | Only checks status 200 |

- **Can pass despite incorrect response data?** YES — all ROUTE_SMOKE/STATUS_ONLY tests
- **Can pass despite no DB persistence?** YES — stubs return hardcoded `{"result": 1}`
- **Only verify HTTP status:** 8 of 24
- **Duplicate coverage:** 4 tests duplicate tests in other files (`test_health_in_*`, `test_version_in_*`)

---

### 4. `tests/api/test_matching.py` — 10 tests

| Function | Category | Notes |
|---|---|---|
| `test_matching_server_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_matching_server_returns_json` | STATUS_ONLY | Only checks content-type |
| `test_matching_server_returns_servers` | ROUTE_SMOKE | `"result" in data` — presence only |
| `test_matching_server_x_galaxy_api_header` | ROUTE_SMOKE | Header presence |
| `test_matching_server_echoes_api_id` | MEANINGFUL_BEHAVIOR | Tests request→response header echo |
| `test_match_id_generate_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_match_id_generate_returns_json` | STATUS_ONLY | Only checks content-type |
| `test_match_id_generate_has_match_id` | ROUTE_SMOKE | `"match_id" in data` — presence only |
| `test_unknown_matching_endpoint_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_unknown_matching_endpoint_returns_result` | ROUTE_SMOKE | `"result" in data` |

- **Can pass despite incorrect response data?** YES — all tests
- **Can pass despite no DB persistence?** YES — stubs
- **Only verify HTTP status:** 5 of 10

---

### 5. `tests/api/test_player.py` — 12 tests

| Function | Category | Notes |
|---|---|---|
| `test_profile_load_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_profile_load_returns_json` | STATUS_ONLY | Only checks content-type |
| `test_profile_load_x_galaxy_api_header` | ROUTE_SMOKE | Header presence |
| `test_login_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_login_returns_json` | STATUS_ONLY | Only checks content-type |
| `test_login_x_galaxy_api_header` | ROUTE_SMOKE | Header presence |
| `test_register_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_register_returns_result` | ROUTE_SMOKE | `"result" in data` |
| `test_login_bonus_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_login_bonus_has_result` | ROUTE_SMOKE | `"result" in data` |
| `test_unknown_player_endpoint_returns_200` | STATUS_ONLY | Only checks status 200 |
| `test_unknown_player_endpoint_returns_result` | ROUTE_SMOKE | `"result" in data` |

- **Can pass despite incorrect response data?** YES — all tests
- **Can pass despite no DB persistence?** YES — stubs
- **Only verify HTTP status:** 6 of 12

---

### 6. `tests/api/test_ranking.py` — 10 tests

| Function | Category | Notes |
|---|---|---|
| `test_ranking_national_returns_200` | STATUS_ONLY | |
| `test_ranking_national_returns_json` | STATUS_ONLY | |
| `test_ranking_location_returns_200` | STATUS_ONLY | |
| `test_ranking_location_returns_json` | STATUS_ONLY | |
| `test_ranking_prefecture_returns_200` | STATUS_ONLY | |
| `test_ranking_prefecture_returns_json` | STATUS_ONLY | |
| `test_ranking_event_returns_200` | STATUS_ONLY | |
| `test_ranking_event_returns_json` | STATUS_ONLY | |
| `test_ranking_weapon_returns_200` | STATUS_ONLY | |
| `test_ranking_weapon_returns_json` | STATUS_ONLY | |

- **Can pass despite incorrect response data?** YES — every test
- **Can pass despite no DB persistence?** YES — stubs
- **Only verify HTTP status:** 10 of 10 (100%)
- **All 10 tests are pure STATUS_ONLY.** Weakest test file.

---

### 7. `tests/api/test_resource.py` — 5 tests

| Function | Category | Notes |
|---|---|---|
| `test_resource_returns_200` | STATUS_ONLY | |
| `test_resource_returns_json` | STATUS_ONLY | |
| `test_resource_x_galaxy_api_header` | ROUTE_SMOKE | Header presence |
| `test_resource_x_galaxy_api_id_echoed` | MEANINGFUL_BEHAVIOR | Tests header echo behavior |
| `test_resource_body_not_required` | MEANINGFUL_BEHAVIOR | Tests endpoint accepts empty body |

- **Only verify HTTP status:** 2 of 5

---

### 8. `tests/api/test_version.py` — 9 tests

| Function | Category | Notes |
|---|---|---|
| `test_version_returns_200` | STATUS_ONLY | |
| `test_version_returns_json` | STATUS_ONLY | |
| `test_version_has_client_version` | ROUTE_SMOKE | Presence check only |
| `test_version_has_data_version` | ROUTE_SMOKE | Presence check only |
| `test_version_has_stage_ids` | ROUTE_SMOKE | Presence + type check |
| `test_version_client_version_is_string` | ROUTE_SMOKE | Type check only |
| `test_version_data_version_is_string` | ROUTE_SMOKE | Type check only |
| `test_version_x_galaxy_api_header` | ROUTE_SMOKE | Header presence |
| `test_version_x_galaxy_api_id_header` | MEANINGFUL_BEHAVIOR | Header echo test |

- **Can pass despite incorrect response data?** YES — all ROUTE_SMOKE tests only check presence/type, not values
- **Only verify HTTP status:** 2 of 9

---

### 9. `tests/protocol/test_codec.py` — 23 tests

| Function | Category | Notes |
|---|---|---|
| `test_encode_zero` | SCHEMA_SYNTHETIC | Tests local helper, not `app.protocol.codec` |
| `test_encode_one` | SCHEMA_SYNTHETIC | |
| `test_encode_127` | SCHEMA_SYNTHETIC | |
| `test_encode_128` | SCHEMA_SYNTHETIC | |
| `test_encode_300` | SCHEMA_SYNTHETIC | |
| `test_roundtrip` (varint) | SCHEMA_SYNTHETIC | |
| `test_encode_short_payload` | SCHEMA_SYNTHETIC | |
| `test_encode_empty_payload` | SCHEMA_SYNTHETIC | |
| `test_decode_short_payload` | SCHEMA_SYNTHETIC | |
| `test_decode_empty_payload` | SCHEMA_SYNTHETIC | |
| `test_roundtrip` (length-prefix) | SCHEMA_SYNTHETIC | |
| `test_decode_too_short_data` | SCHEMA_SYNTHETIC | |
| `test_decode_truncated_payload` | SCHEMA_SYNTHETIC | |
| `test_encode_ping` | SCHEMA_SYNTHETIC | Tests local helper |
| `test_encode_request_entry_matching` | SCHEMA_SYNTHETIC | |
| `test_encode_response_entry_matching` | SCHEMA_SYNTHETIC | |
| `test_encode_notify_match_made` | SCHEMA_SYNTHETIC | |
| `test_encode_notify_match_begin` | SCHEMA_SYNTHETIC | |
| `test_full_wire_format` | SCHEMA_SYNTHETIC | |
| `test_large_packet_id` | SCHEMA_SYNTHETIC | |
| `test_zero_values` | SCHEMA_SYNTHETIC | |
| `test_simulate_cabinet_ping` | SCHEMA_SYNTHETIC | Simulated, not real cabinet traffic |
| `test_simulate_match_entry` | SCHEMA_SYNTHETIC | Simulated |

- **Critical issue:** This entire file defines its own `encode_varint32`, `decode_varint32`, `encode_length_prefixed`, `decode_length_prefixed`, `encode_pb_message`, `decode_pb_message` — all local helpers that **do not import from `app.protocol.codec`**. These tests validate the test's own helpers, not the real codec. If the real codec's varint or framing implementation changes, these tests will still pass.

---

### 10. `tests/protocol/test_generated_pb2.py` — 33 tests

| Function | Category | Notes |
|---|---|---|
| `test_set_packet_id_and_message_type` | SCHEMA_SYNTHETIC | Protobuf generated code roundtrip |
| `test_roundtrip_empty_message` | SCHEMA_SYNTHETIC | |
| `test_large_values` | SCHEMA_SYNTHETIC | |
| `test_zero_values` | SCHEMA_SYNTHETIC | |
| `test_session_id_optional` | SCHEMA_SYNTHETIC | |
| `test_no_session_id_field` | SCHEMA_SYNTHETIC | |
| `test_ping_in_oneof` | SCHEMA_SYNTHETIC | |
| `test_ping_roundtrip` | SCHEMA_SYNTHETIC | |
| `test_ping_empty_body` | SCHEMA_SYNTHETIC | |
| `test_set_message_type_200` | SCHEMA_SYNTHETIC | |
| `test_request_entry_matching_roundtrip` | SCHEMA_SYNTHETIC | |
| `test_real_protobuf_frame_roundtrip` | SCHEMA_SYNTHETIC | Uses real codec encode/decode |
| `test_header_is_4_bytes_le` | SCHEMA_SYNTHETIC | |
| `test_multiple_different_message_sizes` | SCHEMA_SYNTHETIC | |
| `test_incomplete_header` | SCHEMA_SYNTHETIC | Tests real FramingError |
| `test_header_says_more_than_available` | SCHEMA_SYNTHETIC | Tests real FramingError |
| `test_header_only` | SCHEMA_SYNTHETIC | Tests real FramingError |
| `test_extra_trailing_bytes_returned` | SCHEMA_SYNTHETIC | |
| `test_two_consecutive_frames` | SCHEMA_SYNTHETIC | |
| `test_three_frames` | SCHEMA_SYNTHETIC | |
| `test_partial_second_frame` | SCHEMA_SYNTHETIC | |
| `test_oversized_frame_rejected` | SCHEMA_SYNTHETIC | Tests real MAX_MESSAGE_SIZE |
| `test_exactly_max_size_accepted` | SCHEMA_SYNTHETIC | |
| `test_one_over_max_rejected` | SCHEMA_SYNTHETIC | |
| `test_zero_length_frame` | SCHEMA_SYNTHETIC | |
| `test_zero_length_with_trailing` | SCHEMA_SYNTHETIC | |
| `test_roundtrip_empty_pb_message` | SCHEMA_SYNTHETIC | |
| `test_invalid_varint_in_pb` | SCHEMA_SYNTHETIC | Tests protobuf DecodeError |
| `test_random_garbage_fails_parse` | SCHEMA_SYNTHETIC | |
| `test_truncated_field_value` | SCHEMA_SYNTHETIC | |
| `test_bad_wire_type_tag` | SCHEMA_SYNTHETIC | |
| `test_trailing_garbage_rejected` | SCHEMA_SYNTHETIC | |
| `test_valid_protobuf_unknown_fields_ignored` | SCHEMA_SYNTHETIC | |

- **Better than `test_codec.py`** because it imports the real `encode_length_prefix`/`decode_length_prefix` from `app.protocol.codec`. But all 33 tests are SCHEMA_SYNTHETIC — they verify protobuf serialization mechanics, not business logic.

---

### 11. `tests/unit/test_battle_states.py` — 19 tests

| Function | Category | Notes |
|---|---|---|
| `test_created_to_assigned` | MEANINGFUL_BEHAVIOR | **Tests LOCAL copy, not `app.domain.battle`** |
| `test_created_to_cancelled` | MEANINGFUL_BEHAVIOR | |
| `test_assigned_to_waiting_ready` | MEANINGFUL_BEHAVIOR | |
| `test_assigned_to_disconnected` | MEANINGFUL_BEHAVIOR | |
| `test_waiting_ready_to_ready` | MEANINGFUL_BEHAVIOR | |
| `test_waiting_ready_to_expired` | MEANINGFUL_BEHAVIOR | |
| `test_waiting_ready_to_disconnected` | MEANINGFUL_BEHAVIOR | |
| `test_ready_to_running` | MEANINGFUL_BEHAVIOR | |
| `test_ready_to_cancelled` | MEANINGFUL_BEHAVIOR | |
| `test_running_to_result_pending` | MEANINGFUL_BEHAVIOR | |
| `test_running_to_expired` | MEANINGFUL_BEHAVIOR | |
| `test_running_to_disconnected` | MEANINGFUL_BEHAVIOR | |
| `test_result_pending_to_completed` | MEANINGFUL_BEHAVIOR | |
| `test_result_pending_to_failed` | MEANINGFUL_BEHAVIOR | |
| `test_terminal_states_no_transitions` | MEANINGFUL_BEHAVIOR | |
| `test_invalid_transitions` | MEANINGFUL_BEHAVIOR | |
| `test_full_happy_path` | MEANINGFUL_BEHAVIOR | |
| `test_cancelled_before_start` | MEANINGFUL_BEHAVIOR | |
| `test_disconnect_at_any_active_state` | MEANINGFUL_BEHAVIOR | |

- **Critical issue:** Redefines `BattleState` and `VALID_TRANSITIONS` locally instead of importing from `app.domain.battle`. Tests validate a copy, not the real code.

---

### 12. `tests/unit/test_config.py` — 8 tests

| Function | Category | Notes |
|---|---|---|
| `test_default_settings` | MEANINGFUL_BEHAVIOR | Tests real `Settings` defaults |
| `test_custom_port` | MEANINGFUL_BEHAVIOR | |
| `test_production_env` | MEANINGFUL_BEHAVIOR | |
| `test_legacy_compatibility_mode_default` | MEANINGFUL_BEHAVIOR | |
| `test_database_url_stored` | MEANINGFUL_BEHAVIOR | |
| `test_redis_url_stored` | MEANINGFUL_BEHAVIOR | |
| `test_protocol_logging_defaults` | MEANINGFUL_BEHAVIOR | |
| `test_matcher_hostname` | MEANINGFUL_BEHAVIOR | |

- All 8 tests import and test the real `Settings` class. Good coverage.

---

### 13. `tests/unit/test_matching_states.py` — 21 tests

| Function | Category | Notes |
|---|---|---|
| `test_created_to_queued` | MEANINGFUL_BEHAVIOR | **Tests LOCAL copy, not `app.domain.matching`** |
| `test_created_to_cancelled` | MEANINGFUL_BEHAVIOR | |
| `test_queued_to_candidate_found` | MEANINGFUL_BEHAVIOR | |
| `test_queued_to_timed_out` | MEANINGFUL_BEHAVIOR | |
| `test_queued_to_cancelled` | MEANINGFUL_BEHAVIOR | |
| `test_queued_to_disconnected` | MEANINGFUL_BEHAVIOR | |
| `test_candidate_found_to_room_created` | MEANINGFUL_BEHAVIOR | |
| `test_candidate_found_to_disconnected` | MEANINGFUL_BEHAVIOR | |
| `test_candidate_found_to_failed` | MEANINGFUL_BEHAVIOR | |
| `test_room_created_to_waiting_ready` | MEANINGFUL_BEHAVIOR | |
| `test_room_created_to_failed` | MEANINGFUL_BEHAVIOR | |
| `test_waiting_ready_to_ready` | MEANINGFUL_BEHAVIOR | |
| `test_waiting_ready_to_timed_out` | MEANINGFUL_BEHAVIOR | |
| `test_waiting_ready_to_disconnected` | MEANING_BEHAVIOR | |
| `test_waiting_ready_to_cancelled` | MEANINGFUL_BEHAVIOR | |
| `test_ready_to_battle_assigned` | MEANINGFUL_BEHAVIOR | |
| `test_ready_to_disconnected` | MEANINGFUL_BEHAVIOR | |
| `test_battle_assigned_to_disconnected` | MEANINGFUL_BEHAVIOR | |
| `test_terminal_states_no_transitions` | MEANINGFUL_BEHAVIOR | |
| `test_invalid_transitions` | MEANINGFUL_BEHAVIOR | |
| `test_full_happy_path` | MEANINGFUL_BEHAVIOR | |

- **Same critical issue as test_battle_states.py:** Redefines `MatchingState` and `VALID_TRANSITIONS` locally instead of importing from `app.domain.matching`.

---

### 14. `tests/unit/test_protocol_registry.py` — 15 tests

| Function | Category | Notes |
|---|---|---|
| `test_ping_lookup` | MOCK_DOMINATED | Tests local copy of registry, not `app.protocol.registry` |
| `test_request_entry_matching_lookup` | MOCK_DOMINATED | |
| `test_response_entry_matching_lookup` | MOCK_DOMINATED | |
| `test_notify_match_made_lookup` | MOCK_DOMINATED | |
| `test_notify_match_begin_lookup` | MOCK_DOMINATED | |
| `test_burst_group_entry_lookup` | MOCK_DOMINATED | |
| `test_burst_made_lookup` | MOCK_DOMINATED | |
| `test_burst_meets_lookup` | MOCK_DOMINATED | |
| `test_unknown_message_type_returns_none` | MOCK_DOMINATED | |
| `test_zero_returns_none` | MOCK_DOMINATED | |
| `test_negative_returns_none` | MOCK_DOMINATED | |
| `test_all_message_types_registered` | MOCK_DOMINATED | |
| `test_request_types_are_client_to_server` | MOCK_DOMINATED | |
| `test_response_types_are_server_to_client` | MOCK_DOMINATED | |
| `test_notify_types_are_server_to_client` | MOCK_DOMINATED | |

- **Critical issue:** Defines its own `MESSAGE_TYPE_REGISTRY` and `lookup_message_type()` locally. Does **not** import from `app.protocol.registry`. If the real registry changes, these tests still pass.
- All 15 tests are MOCK_DOMINATED — the unit under test is replaced entirely.

---

### 15. `tests/unit/test_tcp_server.py` — 10 tests

| Function | Category | Notes |
|---|---|---|
| `test_stores_handler` | MEANINGFUL_BEHAVIOR | Tests real `register_handler` |
| `test_overwrites_existing` | MEANINGFUL_BEHAVIOR | |
| `test_returns_none` | MEANINGFUL_BEHAVIOR | Tests real `handle_message` |
| `test_returns_framed_payload` | MEANINGFUL_BEHAVIOR | Tests real `_handle_ping` |
| `test_framing_is_4_byte_le` | MEANINGFUL_BEHAVIOR | |
| `test_empty_payload` | MEANINGFUL_BEHAVIOR | |
| `test_is_1_mib` | MEANINGFUL_BEHAVIOR | Tests real `MAX_FRAME_SIZE` |
| `test_dispatch_calls_correct_handler` | MEANINGFUL_BEHAVIOR | Integration: real codec + mock writer |
| `test_unknown_type_gets_default_handler` | MEANINGFUL_BEHAVIOR | |
| `test_eof_disconnects` | MEANINGFUL_BEHAVIOR | |

- All 10 tests import from the real `app.tcp_server`. Good coverage.

---

## Summary of Weaknesses

### Tests that can pass despite incorrect binary response data
All 29 ROUTE_SMOKE and 35 STATUS_ONLY tests would pass even if the response payload was completely wrong. They never assert on actual data values beyond presence checks (`"result" in data`) or trivial equality (`result == 1` on stubs).

### Tests that can pass despite no database persistence
All API tests use the `client` fixture with an in-memory SQLite engine, but most endpoints are stubs returning hardcoded JSON. No test verifies that player data, battle results, or matching state is actually persisted.

### Tests that only verify HTTP status
- `test_health.py`: 2 of 4
- `test_legacy_compat.py`: 8 of 24
- `test_matching.py`: 5 of 10
- `test_player.py`: 6 of 12
- `test_ranking.py`: 10 of 10
- `test_resource.py`: 2 of 5
- `test_version.py`: 2 of 9
- **Total: 35 of 84 API tests are pure STATUS_ONLY**

### Tests that mock the unit under test too heavily
- `test_protocol_registry.py`: All 15 tests define a local copy of the registry instead of importing the real one. Equivalent to mocking the unit under test.
- `test_battle_states.py`: All 19 tests define a local copy of the state machine.
- `test_matching_states.py`: All 21 tests define a local copy of the state machine.

### Tests that duplicate another test without increasing coverage
- `test_legacy_compat.py::test_health_in_legacy_mode` duplicates `test_health.py::test_health_returns_ok`
- `test_legacy_compat.py::test_health_in_non_legacy_mode` duplicates the above with monkeypatch
- `test_legacy_compat.py::test_version_in_legacy_mode` duplicates `test_version.py::test_version_returns_200`
- `test_legacy_compat.py::test_version_in_non_legacy_mode` duplicates the above with monkeypatch
- 4 total duplicate tests

---

## Missing Tests

### Missing failure-path tests for protocol codec
1. **`decode_request` with unknown messageType** — No test sends a valid frame with an unregistered messageType and asserts `UnknownMessageType` is raised.
2. **`_decode_with_generated` with no oneof set** — No test sends a PbMessage with only packetId/messageType but no inner message, to verify `DecodeError("PbMessage has no Message oneof set")`.
3. **`_decode_raw` truncated varint** — No test exercises the `_read_varint` error path for truncated data through the real codec.
4. **`_decode_raw` unexpected wire type** — No test sends a payload with an unsupported wire type through the real codec.
5. **`encode_response` without generated modules** — No test verifies `RuntimeError` is raised when `HAS_GENERATED` is False.
6. **`encode_response` with unknown message type** — No test verifies `ValueError` for unregistered messageType.
7. **`encode_response` with missing generated class** — No test verifies `ValueError` when `getattr(pb_module, inner_class_name)` returns None.

### Missing transaction tests for database operations
1. **Player registration persistence** — No test verifies a registered player can be loaded back.
2. **Battle result persistence** — No test verifies battle results are stored and retrievable.
3. **Profile load after register** — No test chains register → profile/load to verify the round-trip.
4. **Concurrent matching state** — No test verifies matching state transitions under concurrent access.
5. **Database rollback on error** — No test verifies transactions are rolled back on exceptions.
6. **Redis session state** — No test verifies Redis-based session or caching behavior.

### Missing protocol edge-case tests
1. **Maximum varint encoding** — No test for 2^32-1 varint values in the real codec.
2. **Empty PbMessage frame** — No test sends a zero-length protobuf payload through `decode_request`.
3. **Multiple frames in TCP buffer** — No test sends two complete frames in a single `reader.feed_data()` call.
4. **Frame boundary splitting** — No test simulates a frame split across multiple `reader.read()` calls.
5. **PbMessage with sessionId** — No test sends a PbMessage with sessionId set through the full decode path.
6. **Back-to-back oversized frames** — No test sends multiple frames where one exceeds MAX_MESSAGE_SIZE.
7. **Zero-length inner message** — No test sends a PbMessage with an empty oneof message.

### Missing error response tests
1. **Missing required header** — No test sends a request without `x-galaxy-api-id` to verify 400 response.
2. **Invalid JSON body** — No test sends malformed JSON to verify error handling.
3. **Missing required fields** — No test sends requests with missing required fields (e.g., `player_id` for login).
4. **Duplicate registration** — No test verifies behavior when registering an already-registered nesys_id.
5. **Non-existent player login** — No test verifies behavior when logging in with an unknown player_id.
6. **TCP handler exception recovery** — No test verifies the server continues after a handler raises an exception.
