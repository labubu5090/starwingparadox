# Starwing Paradox - Implementation Plan

> Version: 1.0
> Date: 2026-08-25
> Status: Phase 0 COMPLETED, Phase 1 CURRENT

---

## Phase 0: Forensic Audit — COMPLETED

### Scope
Complete analysis of the legacy JavaScript server to understand the Starwing Paradox protocol, database schema, and behavior.

### Inputs
- `legacy-js/` repository (9 commits, ~1,785 JS lines)
- `paradox.sql` schema dump (15 tables, 3201 lines)
- `starwingMessage.proto` (390 lines, ~40 messages)
- `API-NOTES.txt` (reverse-engineering notes)

### Deliverables
- `docs/FORENSIC_AUDIT.md` — Complete audit findings
- `docs/PROTOCOL_MAP.md` — All protobuf message types documented
- `docs/DATABASE_MAP.md` — All 15 tables documented with column types
- `docs/ENDPOINT_MATRIX.md` — HTTP route status matrix
- `docs/SECURITY_AND_RELIABILITY_FINDINGS.md` — Security vulnerabilities catalogued

### Tests
- Manual verification of legacy server behavior
- Schema dump validated against running PostgreSQL instance

### Exit Criteria
- All HTTP endpoints documented with status (IMPLEMENTED/PLACEHOLDER)
- All TCP handlers documented with messageType values
- Database schema fully mapped with types and constraints
- Security findings catalogued with severity levels

### Risks
- None (read-only analysis)

### Rollback
- N/A (no changes made)

### Validation
- All findings cross-referenced between proto, JS, and SQL files
- Legacy server tested against real cabinet behavior (where available)

---

## Phase 1: Python Foundation — CURRENT

### Scope
Establish the Python FastAPI server foundation with basic endpoints, configuration, database connectivity, and test infrastructure.

### Inputs
- Forensic audit findings from Phase 0
- Legacy JS source code
- `paradox.sql` schema

### Deliverables
- `server/` directory with FastAPI application
- Basic HTTP endpoints matching legacy behavior
- SQLAlchemy async database layer
- Configuration via environment variables
- Docker Compose setup
- Test suite foundation
- Protobuf codec (in progress)

### Tests
| Test | Type | Status |
|------|------|--------|
| `test_config.py` | Unit | Config loading from env vars |
| `test_health.py` | API | GET /health, GET /ready |
| `test_version.py` | API | POST /version format |
| `test_resource.py` | API | POST /resource returns JSON |
| `test_matching_states.py` | Unit | State machine transitions |
| `test_battle_states.py` | Unit | State machine transitions |
| `test_protocol_registry.py` | Unit | Message type registry |
| `test_codec.py` | Protocol | Framing and encode/decode |
| `test_player.py` | API | Player endpoints with mock DB |
| `test_matching.py` | API | Matching endpoints |
| `test_ranking.py` | API | Ranking endpoints |

### Exit Criteria
- [x] FastAPI app starts and serves /health
- [x] Configuration loads from environment
- [x] Database connection pool initialized
- [x] All placeholder endpoints return correct JSON format
- [x] Test suite runs with pytest
- [ ] Protobuf codec fully functional
- [ ] All tests passing

### Risks
- Protobuf schema has type aliasing anomalies (messageType 214, 206, 202)
- Legacy uses `body-parser` which accepts both JSON and form-urlencoded

### Rollback
- Git revert to Phase 0 state (docs only)

### Validation
- `ruff check server/` passes
- `mypy server/` passes
- `pytest` all tests green

---

## Phase 2: Player Identity, Profile, Credit, Tutorial, Customization

### Scope
Full player lifecycle: registration, login, profile management, credit system, tutorial progress, and cosmetic customization.

### Inputs
- Legacy `playerProfile.js` (all player operations)
- `paradox.sql` schema (15 player tables)
- `API-NOTES.txt` (request/response formats)

### Deliverables
- Player registration with nesys_id
- Login with session tracking
- Profile load/save with all fields
- Login bonus system (streak-based)
- Credit (virtual currency) management
- Tutorial progress tracking
- Customization: emblems, line colors, titles, mecha sets, weapon sets
- Player options persistence

### Tests
| Test | Type | Description |
|------|------|-------------|
| `test_player_register` | API | Register new player, verify DB row |
| `test_player_login` | API | Login creates session, returns profile |
| `test_player_profile` | API | Profile load returns all fields |
| `test_player_options` | API | Options save/load round-trip |
| `test_player_emblems` | API | Emblem CRUD operations |
| `test_player_mecha_sets` | API | Mecha set configuration |
| `test_player_weapons` | API | Weapon set management |
| `test_login_bonus` | Unit | Streak calculation logic |
| `test_consecutive_login` | Unit | Login day counting (fix legacy bug) |

### Exit Criteria
- Player can register with nesys_id
- Login returns complete profile JSON
- All customization endpoints functional
- Login bonus computed correctly (not faked like legacy)
- No SQL injection vulnerabilities (parameterized queries only)

### Risks
- Legacy `consecutive_login_days` is faked (always 0 or 1)
- No unique index on nesys_id in legacy schema
- `playerRegister` uses dynamic column names from request body

### Rollback
- Revert player-related database migrations
- Disable player endpoints

### Validation
- Compare response format against legacy captures
- Test with both test player IDs (10010, 10011)
- Verify all database writes are transactional

---

## Phase 3: Mission, Ranking, Resources, Progression

### Scope
Mission system, ranking calculations, game resource delivery, and player progression tracking.

### Inputs
- `c_resource.json` (game resource definitions)
- `c_ranking*.json` (ranking data files)
- Mission data from `paradox.sql`
- `API-NOTES.txt` (mission reward format)

### Deliverables
- Mission load/save/progress
- Mission reward distribution
- Ranking calculation (1v1 and 2v2)
- Ranking leaderboard queries (national, prefecture, store, event, weapon)
- Game resource endpoint
- Player progression tracking (tutorial status, unlocks)
- Quest system

### Tests
| Test | Type | Description |
|------|------|-------------|
| `test_mission_load` | API | Load player missions |
| `test_mission_progress` | API | Update mission counters |
| `test_mission_reward` | API | Claim mission rewards |
| `test_ranking_national` | API | National leaderboard |
| `test_ranking_prefecture` | API | Prefecture leaderboard |
| `test_ranking_store` | API | Store leaderboard |
| `test_ranking_weapon` | API | Weapon leaderboard by role |
| `test_resource_load` | API | Resource data delivery |
| `test_progression_save` | API | Progress save/load |

### Exit Criteria
- All ranking endpoints return correct JSON format
- Mission progress tracked accurately
- Rewards distributed atomically
- Resource endpoint serves correct data

### Risks
- Ranking data is static JSON in legacy — need to understand dynamic updates
- Mission reward IDs reference external reward tables not in schema

### Rollback
- Disable ranking/mission endpoints
- Revert mission-related migrations

### Validation
- Compare ranking responses against legacy JSON files
- Test mission progress persistence across sessions

---

## Phase 4: Legacy Battle Request and Result Parity

### Scope
Implement battle result recording with exact legacy response format, plus proper persistence and basic ranking computation.

### Inputs
- `battleRecorder.js` (result format)
- `API-NOTES.txt` (request/response captures)
- Battle result JSON structures

### Deliverables
- `POST /battle/record_2on2` with legacy-compatible response
- Result validation (basic sanity checks)
- Ranking delta computation (replace hardcoded values)
- Mission progress updates from battle results
- Game money distribution
- Battle result persistence to PostgreSQL

### Tests
| Test | Type | Description |
|------|------|-------------|
| `test_battle_record_2on2` | API | Legacy-compatible response format |
| `test_battle_result_fields` | Unit | All required response fields present |
| `test_ranking_delta` | Unit | Correct ranking point calculation |
| `test_mission_update` | Integration | Mission progress updated after battle |
| `test_game_money` | Unit | Correct currency distribution |
| `test_battle_persistence` | Integration | Result saved to database |
| `test_duplicate_prevention` | Unit | Same match_id rejected |

### Exit Criteria
- Response format matches legacy exactly
- Ranking points computed (not hardcoded)
- Results persisted to database
- No data loss on partial failures

### Risks
- Ranking formula is unknown — need to reverse-engineer or approximate
- Legacy returns mission data in battle response — need to understand trigger

### Rollback
- Disable battle recording endpoint
- Revert battle-related migrations

### Validation
- Compare response against legacy API-NOTES.txt captures
- Test with both test player IDs
- Verify database consistency

---

## Phase 5: Matching Engine and Multi-Cabinet Room Coordination

### Scope
Implement the matchmaking queue, candidate selection, room allocation, and burst mode (co-op) room management.

### Inputs
- `burstMode.js` (co-op room logic)
- TCP handler code in `starwing.js`
- `PROTOCOL_MAP.md` (message sequence)

### Deliverables
- Redis-backed matchmaking queue
- Match candidate selection algorithm
- Room allocation and management
- Burst mode (co-op) room CRUD
- TCP message handlers for matching flow
- Match state machine implementation
- Multi-cabinet coordination

### Tests
| Test | Type | Description |
|------|------|-------------|
| `test_match_queue_enqueue` | Unit | Player added to queue |
| `test_match_queue_dequeue` | Unit | Player removed from queue |
| `test_match_candidate_selection` | Unit | Compatible players grouped |
| `test_match_timeout` | Unit | Queue entry expires |
| `test_burst_room_create` | Unit | Co-op room created |
| `test_burst_room_join` | Unit | Player joins room |
| `test_burst_room_list` | Unit | Room list returned |
| `test_burst_room_cleanup` | Unit | Empty rooms removed |
| `test_match_state_transitions` | Unit | All valid state transitions |
| `test_tcp_match_entry` | Protocol | messageType 200 → 201 → 302 → 304 |

### Exit Criteria
- Players can enter matchmaking queue
- Match created when compatible players found
- Burst mode rooms create/join/list work
- All state transitions valid
- No race conditions in room management

### Risks
- Legacy burst mode uses in-memory arrays — no persistence
- Room locking not implemented in legacy
- Proto message type aliasing (214, 206, 202)

### Rollback
- Disable matching endpoints
- Flush Redis queue

### Validation
- Test with multiple concurrent connections
- Verify state machine covers all transitions
- Stress test room management

---

## Phase 6: Full Battle Session Lifecycle

### Scope
Complete battle session from match assignment through result recording, including TCP notifications and state tracking.

### Inputs
- Battle state machine from design doc
- TCP message sequence from protocol map
- Result format from Phase 4

### Deliverables
- Battle session state machine
- TCP notifications for battle lifecycle
- Battle start/end coordination
- Result collection and validation
- Post-battle processing (rankings, rewards, missions)
- Reconnection handling
- Timeout and expiry handling

### Tests
| Test | Type | Description |
|------|------|-------------|
| `test_battle_lifecycle` | Integration | Full CREATE → COMPLETE flow |
| `test_battle_cancel` | Unit | CANCELLED transition |
| `test_battle_disconnect` | Unit | DISCONNECTED transition |
| `test_battle_timeout` | Unit | EXPIRED transition |
| `test_battle_result_submit` | API | Result submission and processing |
| `test_battle_rewards` | Integration | Rewards distributed correctly |
| `test_battle_notifications` | Protocol | TCP messages sent in order |
| `test_battle_reconnect` | Integration | Player reconnects to active battle |

### Exit Criteria
- Full battle lifecycle functional
- All state transitions tested
- TCP notifications sent correctly
- Results processed atomically

### Risks
- TCP reconnection is complex — session resume needed
- Battle timeout values unknown
- No battle replay data available

### Rollback
- Disable battle session management
- Revert battle-related TCP handlers

### Validation
- End-to-end test with simulated cabinet connections
- Verify all state transitions
- Test concurrent battles

---

## Phase 7: Real-Cabinet Validation, Resilience, Deployment, Administration

### Scope
Validation against real arcade cabinet hardware, production hardening, deployment pipeline, and administrative tools.

### Inputs
- Real cabinet hardware (if available)
- Production deployment requirements
- Monitoring requirements

### Deliverables
- Real cabinet compatibility testing
- Rate limiting and DDoS protection
- Comprehensive error handling
- Logging and monitoring
- Health checks and readiness probes
- Docker production configuration
- Database backup/restore scripts
- Administrative API endpoints
- Deployment automation
- Documentation updates

### Tests
| Test | Type | Description |
|------|------|-------------|
| `test_cabinet_connect` | Integration | Real cabinet TCP connection |
| `test_cabinet_match` | Integration | Full match flow with cabinet |
| `test_cabinet_battle` | Integration | Battle result from cabinet |
| `test_rate_limiting` | Unit | Request throttling |
| `test_error_handling` | Unit | Graceful degradation |
| `test_db_backup` | Integration | Backup and restore |
| `test_deployment` | Integration | Docker build and start |

### Exit Criteria
- Real cabinet connects and completes match
- All endpoints handle errors gracefully
- Rate limiting effective
- Monitoring in place
- Deployment documented and automated

### Risks
- Real cabinet availability uncertain
- Network latency may affect timing
- Production database sizing unknown

### Rollback
- Revert to Phase 6 state
- Disable production features

### Validation
- Full cabinet session recorded and replayed
- Load testing with simulated concurrent cabinets
- Security audit completed

---

## Summary Timeline

| Phase | Status | Estimated Duration |
|-------|--------|-------------------|
| Phase 0: Forensic Audit | COMPLETED | 2 days |
| Phase 1: Python Foundation | CURRENT | 1-2 weeks |
| Phase 2: Player Identity | PLANNED | 2 weeks |
| Phase 3: Mission/Ranking | PLANNED | 2 weeks |
| Phase 4: Battle Parity | PLANNED | 2 weeks |
| Phase 5: Matching Engine | PLANNED | 3 weeks |
| Phase 6: Battle Lifecycle | PLANNED | 2 weeks |
| Phase 7: Production | PLANNED | 2 weeks |

**Total estimated**: 14-15 weeks from Phase 1 start

---

## Dependencies

```
Phase 0 ──> Phase 1 ──> Phase 2 ──> Phase 3 ──> Phase 4
                                    └──> Phase 5 ──> Phase 6 ──> Phase 7
```

- Phase 2 depends on Phase 1 (database layer)
- Phase 3 depends on Phase 2 (player data)
- Phase 4 depends on Phase 2 (player data) and Phase 3 (ranking)
- Phase 5 depends on Phase 1 (Redis, TCP server)
- Phase 6 depends on Phase 4 (result recording) and Phase 5 (matching)
- Phase 7 depends on all previous phases
