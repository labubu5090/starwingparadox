"""POST /offline — reachable stand-in for the shipping binary's hardcoded
`http://api.example.com:8080/offline` fallback.

G41/G43: the client rewrites a family of player endpoints (profile load, logout,
login, ...) to this single hardcoded offline URL when running in the limited NESYS
mode. The constant never resolved, so RequestPlayerLogin's POST timed out and the
game went straight to CardError. We now:

  1) rewrite that constant in-memory to http://dev.starwing.jp/mock/offline
     (same 35-char length), and
  2) answer /offline here with a superset response (result + snake/camel profile)
     so whichever parser the client uses can find the fields it reads by name.
"""

import json
import logging
from typing import Any
from urllib.parse import parse_qs

from fastapi import APIRouter, Header, Request, Response

from app.capture.request_capture import capture_request_metadata

router = APIRouter(tags=["offline"])
logger = logging.getLogger(__name__)


def _profile_response(player_id: int, nesys_id: str) -> dict[str, Any]:
    """Superset profile payload: `result` plus both camelCase and snake_case keys."""
    common: dict[str, Any] = {
        "result": 1,
        "playerId": player_id,
        "player_id": player_id,
        "nesysId": nesys_id,
        "nesys_id": nesys_id,
    }
    zero_ints = [
        "rankId", "rank_id", "rankId2on2", "rank_id_2on2",
        "titleId", "title_id", "titleId2on2", "title_id_2on2",
        "buddyId", "buddy_id", "buddyIntimacy", "buddy_intimacy",
        "lineColorId", "line_color_id", "emblemId", "emblem_id",
        "emblemId2on2", "emblem_id_2on2", "matchModeId", "match_mode_id",
        "violationPoint", "violation_point", "birthDay", "birth_day",
        "birthMonth", "birth_month", "mechaSetId", "mecha_set_id",
        "sideWeaponId", "side_weapon_id", "mechaPresetId", "mecha_preset_id",
        "rankPoint", "rank_point", "maxRankId", "max_rank_id",
        "rankPoint2on2", "rank_point_2on2", "maxRankId2on2", "max_rank_id_2on2",
        "sameDayLoginCount", "same_day_login_count", "totalLoginDays",
        "total_login_days", "consecutiveLoginDays", "consecutive_login_days",
        "lastPrefRankingOrderId", "last_pref_ranking_order_id",
        "prefRankingTopPlayerCount", "pref_ranking_top_player_count",
        "officialPlayerTypeId", "official_player_type_id",
    ]
    for key in zero_ints:
        common[key] = 0
    common["playerName"] = "ＮｏＮａｍｅ"
    common["player_name"] = "ＮｏＮａｍｅ"
    common["rankingPrefName"] = "東京"
    common["ranking_pref_name"] = "東京"
    common["lastRankingPrefName"] = "東京"
    common["last_ranking_pref_name"] = "東京"
    common["progresses"] = []
    return common


def _load_body(raw: bytes, content_type: str) -> dict[str, Any]:
    if "json" in content_type.lower():
        try:
            obj = json.loads(raw.decode("utf-8", "replace"))
            return obj if isinstance(obj, dict) else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
    fields = parse_qs(raw.decode("utf-8", "replace"))
    return {k: v[0] for k, v in fields.items()}


DEFAULT_PLAYER_ID = 10009


def _derive_ids(body: dict[str, Any]) -> tuple[int, str]:
    nesys_id = ""
    for key in ("nesys_id", "nesysId", "card_id", "cardId", "nesica_id", "nesicaId", "nesysid"):
        val = body.get(key)
        if val:
            nesys_id = str(val)
            break
    player_id = 0
    for key in ("player_id", "playerId", "playerid"):
        val = body.get(key)
        if val:
            try:
                player_id = int(val)
            except (TypeError, ValueError):
                player_id = 0
            break
    if player_id == 0 and nesys_id:
        try:
            player_id = int(nesys_id) % 0x7FFFFFFF or 1
        except (TypeError, ValueError):
            player_id = 0
    if player_id == 0:
        player_id = DEFAULT_PLAYER_ID
    return player_id, nesys_id


@router.post("/offline")
async def offline_handler(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> dict[str, Any]:
    response.headers["x-galaxy-api"] = "*/*"
    if x_galaxy_api_id:
        response.headers["x-galaxy-api-id"] = x_galaxy_api_id

    raw = await request.body()
    content_type = request.headers.get("content-type") or ""
    body = _load_body(raw, content_type)
    player_id, nesys_id = _derive_ids(body)

    logger.info(
        "POST /offline body_len=%d format=%s player_id=%d nesys_id=%r",
        len(raw),
        "json" if "json" in content_type.lower() else "form",
        player_id,
        nesys_id,
    )
    await capture_request_metadata(request, "/offline", 200, None)
    return _profile_response(player_id, nesys_id)