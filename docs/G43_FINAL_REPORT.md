# G43 Final Report

## Classification: LOCAL_PLAYER_PROFILE_HANDLER_IMPLEMENTED

## Commit: PENDING

## Quality Gates
- **Mypy**: clean (85 files)
- **Ruff server**: clean
- **Tests**: 125 collected, 125 passed, 0 failed, 0 skipped

## Public Repository Analysis

| Repository | URL | License | Restrictions |
|-----------|-----|---------|--------------|
| StarwingParadox | https://github.com/ArcadeMachinist/StarwingParadox | NOT_CONFIRMED | Correlation reference only |
| FakeNesicaService | https://github.com/ArcadeMachinist/FakeNesicaService | NOT_CONFIRMED | Correlation reference only |

No source code was copied. All implementations are independent private-server designs.

## Player Profile Route

### Route: POST /player/profile/load
- **Classification**: GAME_CLIENT_CONFIRMED
- **Evidence**: G40/G41 live captures show game sends `{"nesys_id": "str"}`
- **Handler**: Dedicated FastAPI route (not catch-all)
- **Security**: No NESYS/NESiCA/certificate fields

### Request Schema
```json
{
  "nesys_id": "string (required)"
}
```

### Response Schema
```json
{
  "player_id": 1,
  "nesys_id": "...",
  "player_name": "ＮｏＮａｍｅ",
  "rank_id": 0,
  "rank_id_2on2": 0,
  "title_id": 0,
  "title_id_2on2": 0,
  "buddy_id": 0,
  "buddy_intimacy": 0,
  "line_color_id": 0,
  "emblem_id": 0,
  "line_color_id_2on2": 0,
  "emblem_id_2on2": 0,
  "ranking_pref_name": "東京",
  "last_ranking_pref_name": "東京",
  "match_mode_id": 0,
  "violation_point": 0,
  "birth_day": 1,
  "birth_month": 1,
  "mecha_set_id": 0,
  "side_weapon_id": 0,
  "mecha_preset_id": 0,
  "rank_point": 0,
  "max_rank_id": 0,
  "rank_point_2on2": 0,
  "max_rank_id_2on2": 0,
  "same_day_login_count": 0,
  "total_login_days": 0,
  "consecutive_login_days": 0,
  "progresses": [],
  "last_pref_ranking_order_id": 0,
  "pref_ranking_top_player_count": 0,
  "official_player_type_id": 0
}
```

## Matching Server Reconciliation
- **Route**: POST /matching/server
- **Handler**: Dedicated (not catch-all)
- **Response**: `{"ip_addr": "127.0.0.1:6666"}`
- **Status**: CONFIRMED

## game_data/load Decision
- **Status**: DEFERRED
- **Rationale**: Implement after /player/profile/load is validated live

## api.example.com/offline Decision
- **Status**: UNRESOLVED
- **Rationale**: Game client hardcoded URL, low priority for profile progression

## Security Boundaries Maintained
- No forced bNesysServerLive or IsOnline
- No NESYS certificate fabrication
- No NESiCA identity claims
- No production data usage
- No executable patching
- No named-pipe emulation
- No port 1042 binding

## Next Steps (G44)
1. Live validation of /player/profile/load
2. Card-present event triggering
3. /game_data/load implementation (after profile validation)
