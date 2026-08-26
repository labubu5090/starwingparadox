# Test Quality Audit — Starwing Paradox

**Date:** 2026-08-26
**Total tests:** 414 collected, 392 passed, 22 skipped (integration/DB)
**Coverage:** 39% overall (1462 stmts, 888 miss)

---

## Test Classification Summary

| Category | Count | Description |
|---|---|---|
| **LEGACY_REGRESSION** | 64 | Tests real legacy behavior against source evidence (starwing.js citations) |
| **MEANINGFUL_BEHAVIOR** | 93 | Tests real business logic with real dependencies (FastAPI TestClient) |
| **SCHEMA_SYNTHETIC** | 11 | Tests protobuf schema or message structure comparison |
| **PURE_UNIT** | 86 | Tests pure logic with no I/O (state machines, codec, config) |
| **MOCK_DOMINATED** | 9 | Tests that mock the unit under test heavily (tcp_server unit tests) |
| **REAL_DATABASE_REQUIRED** | 21 | Tests need real PostgreSQL (skipped when TEST_DATABASE_URL unset) |
| **REAL_CAPTURE_REQUIRED** | 0 | No tests require real cabinet capture hardware |

---

## Detailed Classification by File

### tests/api/ (65 tests)

| File | Test | Category | Notes |
|---|---|---|---|
| test_health.py | test_health_returns_ok | MEANINGFUL_BEHAVIOR | Checks status + body field |
| test_health.py | test_health_returns_json | MEANINGFUL_BEHAVIOR | Content-type check |
| test_health.py | test_ready_returns_status | MEANINGFUL_BEHAVIOR | Checks status + body value |
| test_health.py | test_ready_returns_json | MEANINGFUL_BEHAVIOR | Content-type check |
| test_version.py | test_version_returns_200 | MEANINGFUL_BEHAVIOR | Status + body structure + field count |
| test_version.py | test_version_returns_json | MEANINGFUL_BEHAVIOR | Content-type check |
| test_version.py | test_version_has_client_version | MEANINGFUL_BEHAVIOR | Field + value assertion |
| test_version.py | test_version_has_data_version | MEANINGFUL_BEHAVIOR | Field + value assertion |
| test_version.py | test_version_has_stage_ids | MEANINGFUL_BEHAVIOR | Field + type + value |
| test_version.py | test_version_client_version_is_string | MEANINGFUL_BEHAVIOR | Type assertion |
| test_version.py | test_version_data_version_is_string | MEANINGFUL_BEHAVIOR | Type assertion |
| test_version.py | test_version_x_galaxy_api_header | MEANINGFUL_BEHAVIOR | Header + value |
| test_version.py | test_version_x_galaxy_api_id_header | MEANINGFUL_BEHAVIOR | Header echo |
| test_resource.py | test_resource_returns_200 | MEANINGFUL_BEHAVIOR | Status + body type |
| test_resource.py | test_resource_returns_json | MEANINGFUL_BEHAVIOR | Content-type |
| test_resource.py | test_resource_x_galaxy_api_header | MEANINGFUL_BEHAVIOR | Header + value |
| test_resource.py | test_resource_x_galaxy_api_id_echoed | MEANINGFUL_BEHAVIOR | Header echo |
| test_resource.py | test_resource_body_not_required | MEANINGFUL_BEHAVIOR | Status + body type |
| test_matching.py | test_matching_server_returns_200 | MEANINGFUL_BEHAVIOR | Status check |
| test_matching.py | test_matching_server_returns_json | MEANINGFUL_BEHAVIOR | Content-type |
| test_matching.py | test_matching_server_returns_ip_addr | MEANINGFUL_BEHAVIOR | Field + type + format |
| test_matching.py | test_matching_server_no_result_field | MEANINGFUL_BEHAVIOR | Negative assertion |
| test_matching.py | test_matching_server_x_galaxy_api_header | MEANINGFUL_BEHAVIOR | Header presence |
| test_matching.py | test_matching_server_echoes_api_id | MEANINGFUL_BEHAVIOR | Header echo |
| test_matching.py | test_match_id_generate_returns_200 | MEANINGFUL_BEHAVIOR | Status |
| test_matching.py | test_match_id_generate_returns_json | MEANINGFUL_BEHAVIOR | Content-type |
| test_matching.py | test_match_id_generate_returns_int | MEANINGFUL_BEHAVIOR | Field + type + range |
| test_matching.py | test_match_id_generate_no_result_field | MEANINGFUL_BEHAVIOR | Negative assertion |
| test_matching.py | test_unknown_matching_endpoint_returns_200 | MEANINGFUL_BEHAVIOR | Status + content-type |
| test_matching.py | test_unknown_matching_endpoint_returns_empty | MEANINGFUL_BEHAVIOR | Body equality |
| test_matching.py | test_unknown_matching_endpoint_no_result | MEANINGFUL_BEHAVIOR | Negative assertion |
| test_player.py | test_profile_load_returns_200 | MEANINGFUL_BEHAVIOR | Status + body type + result field |
| test_player.py | test_profile_load_returns_json | MEANINGFUL_BEHAVIOR | Content-type |
| test_player.py | test_profile_load_x_galaxy_api_header | MEANINGFUL_BEHAVIOR | Header + value |
| test_player.py | test_login_returns_200 | MEANINGFUL_BEHAVIOR | Status + body type + result field |
| test_player.py | test_login_returns_json | MEANINGFUL_BEHAVIOR | Content-type |
| test_player.py | test_login_x_galaxy_api_header | MEANINGFUL_BEHAVIOR | Header + value |
| test_player.py | test_register_returns_200 | MEANINGFUL_BEHAVIOR | Status + body + content-type |
| test_player.py | test_register_returns_result | MEANINGFUL_BEHAVIOR | Field check |
| test_player.py | test_login_bonus_returns_200 | MEANINGFUL_BEHAVIOR | Status + body + content-type |
| test_player.py | test_login_bonus_has_result | MEANINGFUL_BEHAVIOR | Field check |
| test_player.py | test_unknown_player_endpoint_returns_200 | MEANINGFUL_BEHAVIOR | Status + body + result |
| test_player.py | test_unknown_player_endpoint_returns_result | MEANINGFUL_BEHAVIOR | Field check |
| test_ranking.py | test_ranking_national_returns_501 | MEANINGFUL_BEHAVIOR | Status + body type + error |
| test_ranking.py | test_ranking_national_returns_not_implemented | MEANINGFUL_BEHAVIOR | Error + endpoint |
| test_ranking.py | test_ranking_national_x_legacy_compat | MEANINGFUL_BEHAVIOR | Header + content-type |
| test_ranking.py | test_ranking_location_returns_501 | MEANINGFUL_BEHAVIOR | Status + body type + error |
| test_ranking.py | test_ranking_location_returns_not_implemented | MEANINGFUL_BEHAVIOR | Error + endpoint + content-type |
| test_ranking.py | test_ranking_prefecture_returns_501 | MEANINGFUL_BEHAVIOR | Status + body type + error |
| test_ranking.py | test_ranking_prefecture_returns_not_implemented | MEANINGFUL_BEHAVIOR | Error + endpoint + content-type |
| test_ranking.py | test_ranking_event_returns_501 | MEANINGFUL_BEHAVIOR | Status + body type + error |
| test_ranking.py | test_ranking_event_returns_not_implemented | MEANINGFUL_BEHAVIOR | Error + endpoint + content-type |
| test_ranking.py | test_ranking_weapon_returns_501 | MEANINGFUL_BEHAVIOR | Status + body type + error |
| test_ranking.py | test_ranking_weapon_returns_not_implemented | MEANINGFUL_BEHAVIOR | Error + endpoint + content-type |
| test_ranking.py | test_unknown_ranking_returns_200 | MEANINGFUL_BEHAVIOR | Status + content-type |
| test_ranking.py | test_unknown_ranking_returns_empty | MEANINGFUL_BEHAVIOR | Body equality |
| test_battle.py | test_record_2on2_returns_501 | MEANINGFUL_BEHAVIOR | Status + body type + error |
| test_battle.py | test_record_2on2_returns_not_implemented | MEANINGFUL_BEHAVIOR | Error + endpoint |
| test_battle.py | test_record_2on2_no_result_field | MEANINGFUL_BEHAVIOR | Negative assertion |
| test_battle.py | test_record_2on2_no_success_claim | MEANINGFUL_BEHAVIOR | Negative assertion |
| test_battle.py | test_record_2on2_x_legacy_compat | MEANINGFUL_BEHAVIOR | Header |
| test_battle.py | test_record_2on2_has_corrid | MEANINGFUL_BEHAVIOR | Field + type + length |
| test_battle.py | test_unknown_battle_returns_200 | MEANINGFUL_BEHAVIOR | Status + content-type |
| test_battle.py | test_unknown_battle_returns_result | MEANINGFUL_BEHAVIOR | Body type + result value |
| test_game_data.py | test_load_returns_501 | MEANINGFUL_BEHAVIOR | Status + body type + error |
| test_game_data.py | test_load_returns_not_implemented | MEANINGFUL_BEHAVIOR | Error + endpoint |
| test_game_data.py | test_load_no_result_field | MEANINGFUL_BEHAVIOR | Negative assertion |
| test_game_data.py | test_load_x_legacy_compat | MEANINGFUL_BEHAVIOR | Header + content-type |
| test_game_data.py | test_load_mission_returns_501 | MEANINGFUL_BEHAVIOR | Status + body type + error |
| test_game_data.py | test_load_mission_returns_not_implemented | MEANINGFUL_BEHAVIOR | Error + endpoint |
| test_game_data.py | test_load_mission_no_result_field | MEANINGFUL_BEHAVIOR | Negative + content-type |
| test_game_data.py | test_save_returns_501 | MEANINGFUL_BEHAVIOR | Status + body type + error |
| test_game_data.py | test_save_returns_not_implemented | MEANINGFUL_BEHAVIOR | Error + endpoint |
| test_game_data.py | test_save_no_result_without_persistence | MEANINGFUL_BEHAVIOR | Negative assertion |
| test_game_data.py | test_save_x_legacy_compat | MEANINGFUL_BEHAVIOR | Header + content-type |
| test_game_data.py | test_save_has_corrid | MEANINGFUL_BEHAVIOR | Field + type + length |
| test_game_data.py | test_unknown_game_data_returns_200 | MEANINGFUL_BEHAVIOR | Status |
| test_game_data.py | test_unknown_game_data_returns_result | MEANINGFUL_BEHAVIOR | Result value |
| test_credit.py | test_credit_returns_200 | MEANINGFUL_BEHAVIOR | Status + content-type |
| test_credit.py | test_credit_returns_empty | MEANINGFUL_BEHAVIOR | Body equality |
| test_credit.py | test_credit_no_result_field | MEANINGFUL_BEHAVIOR | Negative assertion |
| test_credit.py | test_credit_no_success_without_processing | MEANINGFUL_BEHAVIOR | Negative assertion |
| test_credit.py | test_credit_purchase_returns_empty | MEANINGFUL_BEHAVIOR | Status + body + content-type |
| test_credit.py | test_credit_history_returns_empty | MEANINGFUL_BEHAVIOR | Status + body + content-type |
| test_legacy_compat.py | (37 tests) | MEANINGFUL_BEHAVIOR | All check status + body + headers |

### tests/protocol/ (56 tests)

| File | Tests | Category |
|---|---|---|
| test_codec.py | 20 tests | PURE_UNIT — varint, framing, pb encoding |
| test_generated_pb2.py | 25 tests | PURE_UNIT — protobuf construction, framing, edge cases |
| test_legacy_proto_compatibility.py | 11 tests | SCHEMA_SYNTHETIC — proto file vs generated descriptor comparison |

### tests/unit/ (66 tests)

| File | Tests | Category |
|---|---|---|
| test_battle_states.py | 18 tests | PURE_UNIT — state machine transitions |
| test_config.py | 8 tests | PURE_UNIT — Settings instantiation |
| test_matching_states.py | 17 tests | PURE_UNIT — state machine transitions |
| test_protocol_registry.py | 14 tests | PURE_UNIT — message type lookup |
| test_tcp_server.py | 9 tests | MOCK_DOMINATED — uses AsyncMock, MagicMock |

### tests/legacy_regression/ (125 tests)

| File | Tests | Category |
|---|---|---|
| test_version_legacy.py | 13 tests | LEGACY_REGRESSION — source citations, exact value checks |
| test_resource_legacy.py | 10 tests | LEGACY_REGRESSION — source citations, conditional assertions |
| test_player_legacy.py | 8 tests | LEGACY_REGRESSION — source citations, known deviation documented |
| test_game_data_legacy.py | 12 tests | LEGACY_REGRESSION — source citations, mode-dependent behavior |
| test_matching_legacy.py | 10 tests | LEGACY_REGRESSION — source citations, mode-dependent behavior |
| test_battle_legacy.py | 10 tests | LEGACY_REGRESSION — source citations, false-success prevention |
| test_tcp_legacy.py | 41 tests | LEGACY_REGRESSION — source citations (E6-E342), framing, protections |

### tests/test_compare_responses.py (15 tests)

| Tests | Category |
|---|---|
| 15 tests | PURE_UNIT — snapshot comparison, protobuf decode, fixture loading |

### tests/integration/ (21 tests)

| Tests | Category |
|---|---|
| 21 tests | REAL_DATABASE_REQUIRED — all skipped without TEST_DATABASE_URL |

---

## STATUS_ONLY Tests Identified (pre-improvement)

These tests originally checked only HTTP status code with no body/header/value assertions:

| File | Test | Improvement Applied |
|---|---|---|
| test_player.py::test_profile_load_returns_200 | Added body type + result field check | ✅ |
| test_player.py::test_login_returns_200 | Added body type + result field check | ✅ |
| test_player.py::test_register_returns_200 | Added body type + result + content-type | ✅ |
| test_player.py::test_login_bonus_returns_200 | Added body type + result + content-type | ✅ |
| test_player.py::test_unknown_player_endpoint_returns_200 | Added body type + result check | ✅ |
| test_resource.py::test_resource_returns_200 | Added body type check | ✅ |
| test_resource.py::test_resource_body_not_required | Added body type check | ✅ |
| test_ranking.py::test_ranking_national_returns_501 | Added body type + error check | ✅ |
| test_ranking.py::test_ranking_location_returns_501 | Added body type + error check | ✅ |
| test_ranking.py::test_ranking_prefecture_returns_501 | Added body type + error check | ✅ |
| test_ranking.py::test_ranking_event_returns_501 | Added body type + error check | ✅ |
| test_ranking.py::test_ranking_weapon_returns_501 | Added body type + error check | ✅ |
| test_ranking.py::test_unknown_ranking_returns_200 | Added content-type check | ✅ |
| test_battle.py::test_record_2on2_returns_501 | Added body type + error check | ✅ |
| test_battle.py::test_record_2on2_has_corrid | Added type + length assertion | ✅ |
| test_battle.py::test_unknown_battle_returns_200 | Added content-type check | ✅ |
| test_game_data.py::test_load_returns_501 | Added body type + error check | ✅ |
| test_game_data.py::test_load_x_legacy_compat | Added content-type check | ✅ |
| test_game_data.py::test_load_mission_returns_501 | Added body type + error check | ✅ |
| test_game_data.py::test_load_mission_no_result_field | Added content-type check | ✅ |
| test_game_data.py::test_save_returns_501 | Added body type + error check | ✅ |
| test_game_data.py::test_save_x_legacy_compat | Added content-type check | ✅ |
| test_game_data.py::test_save_has_corrid | Added type + length assertion | ✅ |

### Enhancement Summary

For each improved test, assertions were added for:
1. **Response body structure** — `isinstance(data, dict)` + key field presence
2. **Content-type header** — `assert "application/json" in response.headers["content-type"]`
3. **Required headers** — header value assertions (e.g., `x-galaxy-api: */*`)
4. **Response field values** — exact value checks where applicable

---

## Bug Found During Audit

**test_health.py::test_ready_returns_status** — Original test asserted `data["status"] == "ok"` but the `/ready` endpoint returns `"ready"`. Fixed to `assert data["status"] == "ready"`.

---

## Coverage Report

### High Coverage (>80%)
| Module | Coverage |
|---|---|
| app/api/matching.py | 100% |
| app/api/version.py | 100% |
| app/config.py | 100% |
| app/protocol/registry.py | 100% |
| app/protocol/errors.py | 100% |
| app/middleware/protocol_logging.py | 100% |
| app/middleware/request_id.py | 100% |
| app/api/battle.py | 97% |
| app/api/game_data.py | 97% |
| app/api/ranking.py | 96% |
| app/api/tutorial.py | 96% |
| app/api/player.py | 90% |
| app/api/resource.py | 87% |
| app/main.py | 84% |
| app/api/health.py | 80% |

### Low Coverage (<50%) — Requires Real DB/External Services
| Module | Coverage | Reason |
|---|---|---|
| app/db/* (all models) | 0% | Requires real PostgreSQL |
| app/db/repositories/* | 0% | Requires real PostgreSQL |
| app/db/session.py | 0% | Requires real PostgreSQL |
| app/services/* | 0% | Requires real PostgreSQL + Redis |
| app/domain/* | 0% | Requires real database models |
| app/api/mission.py | 48% | Partial stub implementation |
| app/protocol/codec.py | 49% | Many error paths untested |
| app/logging_config.py | 41% | Configuration-dependent paths |

### Coverage Stability
Coverage remained at **39%** (1462 stmts, 888 miss) before and after improvements. The STATUS_ONLY test improvements added assertions but did not execute new code paths — they strengthened existing test assertions without changing branch coverage.

---

## Recommendations

1. **Set up TEST_DATABASE_URL** in CI to enable the 21 integration tests (currently skipped)
2. **Add unit tests for app/services/** — player_service, matching_service, battle_service have 0% coverage
3. **Add unit tests for app/db/repositories/** — game_data_repository (193 stmts) and player_repository (28 stmts) are untested
4. **Register custom pytest marks** — `pytest.mark.db` and `pytest.mark.tcp` generate warnings
5. **Fix deprecation** — `asyncio.get_event_loop()` in test_tcp_legacy.py:351 should use `asyncio.run()`
6. **Consider adding app/api/mission.py tests** — only 48% coverage, lowest among API modules
