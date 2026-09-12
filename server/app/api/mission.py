"""Mission endpoints (POST /mission/*)."""

import csv
import json
import logging
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_db_session

router = APIRouter(tags=["mission"], prefix="/mission")
logger = logging.getLogger(__name__)

SWDATA_PATH = Path(__file__).resolve().parents[2] / "sw-data"

_REWARD_CSV: dict[int, tuple[int, int, int]] | None = None


def _load_reward_csv() -> dict[int, tuple[int, int, int]]:
    """Load Reward.csv: reward_id -> (item_type_id, item_id, count)."""
    global _REWARD_CSV
    if _REWARD_CSV is not None:
        return _REWARD_CSV
    mapping: dict[int, tuple[int, int, int]] = {}
    path = SWDATA_PATH / "Reward.csv"
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                reward_id = row.get("RewardId")
                if not reward_id or not reward_id.isdigit():
                    continue
                try:
                    mapping[int(reward_id)] = (
                        int(row.get("ItemTypeId", 0) or 0),
                        int(row.get("ItemId", 0) or 0),
                        int(row.get("Count", 0) or 0),
                    )
                except ValueError:
                    continue
    except FileNotFoundError:
        logger.warning("Reward.csv not found at %s", path)
    _REWARD_CSV = mapping
    return mapping


async def _parse_request_body(request: Request) -> dict:
    raw = await request.body()
    content_type = (request.headers.get("content-type") or "").lower()
    if "json" in content_type:
        try:
            return json.loads(raw.decode("utf-8", "replace"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
    fields = parse_qs(raw.decode("utf-8", "replace"))
    return {k: v[0] if len(v) == 1 else v for k, v in fields.items()}


def _not_implemented(endpoint: str, headers: dict[str, Any] | None = None) -> JSONResponse:
    resp_headers = {"x-legacy-compat": "false"}
    if headers:
        resp_headers.update(headers)
    return JSONResponse(
        status_code=501,
        content={"error": "not_implemented", "endpoint": endpoint, "corrid": str(uuid.uuid4())},
        headers=resp_headers,
    )


def _galaxy_headers(x_galaxy_api_id: str) -> dict[str, str]:
    headers = {"x-galaxy-api": "*/*"}
    if x_galaxy_api_id:
        headers["x-galaxy-api-id"] = x_galaxy_api_id
    return headers


@router.post("/normal")
async def mission_normal(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    missions: list[dict[str, Any]] = []
    try:
        body = await _parse_request_body(request)
        player_id = body.get("player_id")
        if player_id:
            from app.db.repositories.game_data_repository import GameDataRepository
            repo = GameDataRepository(db)
            missions = [
                {"mission_id": m.mission_id, "clear_count": m.clear_count, "clear_num": m.clear_num, "status": m.status, "mission_status": m.mission_status}
                for m in await repo.get_missions(int(player_id))
            ]
    except Exception as exc:
        logger.warning("mission/normal DB error: %s", exc)
    return JSONResponse(
        content={
            "missions": missions,
            "update_items": {"game_moneys": []},
            "normal_mission_reward_ids": [],
            "buddy_normal_mission_reward_ids": [],
            "result": 1,
        },
        headers=headers,
    )


@router.post("/reward/get")
async def mission_reward_get(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    """Process a mission reward claim.

    Request body (captured): {player_id, mission_id, mission_reward_ids}
    where mission_reward_ids is a JSON-encoded array string like "[7102551]".
    The client waits for intimacy_reward_ids, update_items and update_missions
    (starwing.js:599-600); without them it hangs in
    MissionMainModeRewardDrawWait and re-offers the same reward forever.

    Each reward id maps via Reward.csv (ItemTypeId 7 = player title,
    ItemId = title_id). Granted titles, and the mission is marked drawn
    (status=0, mission_status=401) matching the client's own enum:
    ACPP_MissionMain::SetListInfoWidget (exe 0x142ac210d) switches on
    mission_status -- 400 is still claimable (play the draw), any other
    value (201/0) is a normal in-progress mission whose list entry
    re-offers the draw, and 401 (=0x190+1) displays the "reward already
    received" string (このミッションは報酬受け取り済みです). So drawn
    missions must be 401, otherwise the client keeps re-offering.
    """
    headers = _galaxy_headers(x_galaxy_api_id)
    try:
        body = await _parse_request_body(request)
        player_id = body.get("player_id")
        mission_id = body.get("mission_id")
        if not player_id or not mission_id:
            return JSONResponse(
                content={"result": 0, "intimacy_reward_ids": [], "update_items": {}, "update_missions": []},
                headers=headers,
            )

        from app.db.repositories.game_data_repository import GameDataRepository

        repo = GameDataRepository(db)
        player_id_int = int(player_id)

        reward_ids = _safe_list(body.get("mission_reward_ids", "[]"))
        rewards = _load_reward_csv()

        update_items: dict[str, Any] = {}
        game_moneys: list[dict[str, Any]] = []
        for rid_raw in reward_ids:
            try:
                rid = int(rid_raw)
            except (TypeError, ValueError):
                continue
            item = rewards.get(rid)
            if item is None:
                continue
            item_type, item_id, count = item
            if item_type == 7:
                await repo.upsert_title(player_id_int, item_id, 0)
            elif item_type == 1:
                game_moneys.append({"game_money_id": item_id, "count": count})
        update_items["game_moneys"] = game_moneys

        mission = await repo.get_mission(player_id_int, int(mission_id))
        if mission is not None:
            await repo.upsert_mission(
                player_id_int,
                int(mission_id),
                mission.clear_count or 0,
                mission.clear_num or 0,
                0,
                401,
            )
            drawn_mission = {
                "mission_id": int(mission_id),
                "clear_count": mission.clear_count or 0,
                "clear_num": mission.clear_num or 0,
                "status": 0,
                "mission_status": 401,
            }
        else:
            await repo.upsert_mission(
                player_id_int,
                int(mission_id),
                0,
                0,
                0,
                401,
            )
            drawn_mission = {
                "mission_id": int(mission_id),
                "clear_count": 0,
                "clear_num": 0,
                "status": 0,
                "mission_status": 401,
            }

        await db.commit()
        logger.info(
            "mission/reward/get: player=%s mission=%s reward_ids=%s drawn",
            player_id, mission_id, reward_ids,
        )
        return JSONResponse(
            content={
                "result": 1,
                "intimacy_reward_ids": [],
                "update_items": update_items,
                "update_missions": [drawn_mission],
            },
            headers=headers,
        )
    except Exception as exc:
        logger.warning("mission/reward/get error: %s", exc)
        return JSONResponse(
            content={"result": 0, "intimacy_reward_ids": [], "update_items": {}, "update_missions": []},
            headers=headers,
        )


def _safe_list(raw: Any) -> list:
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return [raw]
        return parsed if isinstance(parsed, list) else [raw]
    if isinstance(raw, list):
        return raw
    return [raw]


@router.post("/{path:path}")
async def mission_fallback(
    path: str,
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    logger.debug("Unimplemented mission endpoint: /mission/%s", path)
    if not settings.legacy_compatibility_mode:
        return _not_implemented(f"/mission/{path}", headers)
    return JSONResponse(content={}, headers=headers)
