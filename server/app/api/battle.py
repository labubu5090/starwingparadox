"""Battle endpoints (POST /battle/*) - rank/record handling."""

import csv
import logging
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models.player import Player
from app.dependencies import get_db_session

router = APIRouter(tags=["battle"], prefix="/battle")
logger = logging.getLogger(__name__)

_SW_DATA_DIR = Path(settings.get_database_url() and settings.database_url)
# CSV live under server/sw-data next to the repo; resolve relative to this file.
_CSV_DIR = Path(__file__).resolve().parents[2] / "sw-data"

# BattleResultId 1 = win (+RankPoint), 2 = lose (+RankPoint per CSV).
_BATTLE_RESULT_RANK_POINT: dict[int, int] = {}
try:
    with (_CSV_DIR / "BattleResultRankPoint.csv").open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            try:
                key = int(row["BattleResultId"])
            except (KeyError, ValueError):
                continue
            try:
                val = int(row["BattleResultRankPoint"])
            except (KeyError, ValueError):
                val = 0
            _BATTLE_RESULT_RANK_POINT[key] = val
except FileNotFoundError:
    _BATTLE_RESULT_RANK_POINT = {1: 800, 2: 0}

_RANK_RANGES: list[tuple[int, int, int]] = []  # (rank_id, initial, required)
try:
    with (_CSV_DIR / "Rank.csv").open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            try:
                rid = int(row["Id"])
                initial = int(row["InitialPoint"])
                required = int(row["RequiredPoint"])
            except (KeyError, ValueError):
                continue
            _RANK_RANGES.append((rid, initial, required))
except FileNotFoundError:
    _RANK_RANGES = []

_RANK_RANGES.sort(key=lambda r: r[0])


def _rank_for_point(rank_point: int) -> int:
    """Return the highest rank_id whose initial requirement the point meets."""
    current = 1
    for rid, initial, _required in _RANK_RANGES:
        if rank_point >= initial:
            current = rid
        else:
            break
    return current


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


async def _parse_form_body(request: Request) -> dict[str, str]:
    raw = await request.body()
    fields = parse_qs(raw.decode("utf-8", "replace"))
    return {k: v[0] if len(v) == 1 else v for k, v in fields.items()}


async def _resolve_player(db: AsyncSession, player_id: Any) -> Player | None:
    try:
        pid = int(player_id)
    except (TypeError, ValueError):
        return None
    result = await db.execute(select(Player).where(Player.player_id == pid))
    return result.scalar_one_or_none()


async def _player_missions(db: AsyncSession, player_id: int) -> list[dict[str, Any]]:
    result = await db.execute(
        text(
            "SELECT mission_id, clear_count, clear_num, status, mission_status "
            "FROM player_missions WHERE player_id = :pid"
        ),
        {"pid": player_id},
    )
    rows = result.fetchall()
    return [
        {
            "mission_id": r[0],
            "clear_count": r[1],
            "clear_num": r[2],
            "status": r[3],
            "mission_status": r[4],
        }
        for r in rows
    ]


def _update_items(game_money_count: int = 0) -> dict[str, Any]:
    game_moneys: list[dict[str, Any]] = []
    if game_money_count:
        game_moneys.append({"game_money_id": 1, "count": game_money_count})
    return {"game_moneys": game_moneys}


@router.post("/record")
async def battle_record(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    """Record a battle result and return rank/score progression data.

    Mirrors legacy-js BattleRecorder.battleRecord2on2, but for the solo
    /battle/record endpoint the client actually calls. Persists rank_point
    (win +800 / lose +0 per BattleResultRankPoint.csv) so rank survives
    restarts; the response carries every field the client parses, ending the
    "data not accumulating / rank reset to 0" loop.
    """
    body = await _parse_form_body(request)
    player_id = body.get("player_id", "")
    battle_result = (body.get("battle_result") or "").lower()
    is_win = battle_result in ("win", "1", "true")

    winning_streaks = 1
    gained_rank_point = _BATTLE_RESULT_RANK_POINT.get(1 if is_win else 2, 0)

    player = await _resolve_player(db, player_id)
    old_rank_point = 0
    if player is not None:
        old_rank_point = player.rank_point or 0
        new_point = old_rank_point + gained_rank_point
        player.rank_point = new_point
        player.rank_id = _rank_for_point(new_point)
        if player.max_rank_id is None or player.rank_id > player.max_rank_id:
            player.max_rank_id = player.rank_id
        try:
            await db.commit()
            logger.info(
                "battle/record player_id=%s result=%s rank_point %d->%d rank_id=%d",
                player_id, battle_result, old_rank_point, new_point, player.rank_id,
            )
        except Exception as exc:
            logger.warning("battle/record DB commit failed: %s", exc)
            await db.rollback()
        old_rank_point = new_point

    payload = {
        "winning_streaks": winning_streaks,
        "rank_point": old_rank_point,
        "battle_result_rank_point": gained_rank_point,
        "ranking_score": old_rank_point,
        "ranking_high_score": max(old_rank_point, old_rank_point),
        "gained_ranking_score": gained_rank_point,
        "is_update_rank_point": gained_rank_point > 0,
        "is_update_ranking_score": gained_rank_point > 0,
        "is_up_ranking_score": gained_rank_point > 0,
        "is_new_record_ranking_score": True,
        "update_items": _update_items(gained_rank_point // 10),
        "battle_reward_ids": [],
        "rank_up_reward_ids": [],
        "rank_point_reward_ids": [],
        "intimacy_up_reward_ids": [],
        "avg_minute_score": {
            "stage_id": body.get("stage_id", ""),
            "rank_id": 1,
            "avg_minute_score": 0,
        },
    }
    if player is not None:
        payload["missions"] = await _player_missions(db, player.player_id)

    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/battle/record", headers)
    resp = JSONResponse(content=payload, headers=headers)
    response.headers.update(headers)
    return resp


@router.post("/skip_rank")
async def battle_skip_rank(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    """Persist the rank the client computed after battle + reward wrap-up."""
    body = await _parse_form_body(request)
    player = await _resolve_player(db, body.get("player_id"))
    if player is not None:
        try:
            rank_id = int(body.get("rank_id", player.rank_id or 0))
            rank_point = int(body.get("rank_point", player.rank_point or 0))
        except (TypeError, ValueError):
            rank_id = None
            rank_point = None
        if rank_id is not None and rank_point is not None:
            player.rank_id = rank_id
            player.rank_point = rank_point
            try:
                await db.commit()
                logger.info(
                    "battle/skip_rank player_id=%s rank_id=%d rank_point=%d",
                    body.get("player_id"), rank_id, rank_point,
                )
            except Exception as exc:
                logger.warning("battle/skip_rank DB commit failed: %s", exc)
                await db.rollback()

    payload = {
        "result": 1,
        "update_items": _update_items(),
        "battle_reward_ids": [],
        "rank_up_reward_ids": [],
        "rank_point_reward_ids": [],
        "intimacy_up_reward_ids": [],
    }
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/battle/skip_rank", headers)
    resp = JSONResponse(content=payload, headers=headers)
    response.headers.update(headers)
    return resp


@router.post("/record_2on2")
async def battle_record_2on2(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/battle/record_2on2", headers)
    return JSONResponse(content={"result": 1}, headers=headers)


@router.post("/{path:path}")
async def battle_fallback(
    path: str,
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    logger.debug("Unimplemented battle endpoint: /battle/%s", path)
    if not settings.legacy_compatibility_mode:
        return _not_implemented(f"/battle/{path}", headers)
    return JSONResponse(content={"result": 1}, headers=headers)