"""Player-related endpoints (login, profile, register, logout, etc.)."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.capture.request_capture import capture_request_metadata
from app.config import settings
from app.db.models.player import Player
from app.dependencies import get_db_session

router = APIRouter(tags=["player"], prefix="/player")
logger = logging.getLogger(__name__)


def _ok(result: int = 1, **extra: Any) -> dict[str, Any]:
    return {"result": result, **extra}


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


async def _get_active_profile_uuid(db: AsyncSession) -> str | None:
    from app.db.repositories.local_profile_repository import LocalProfileRepository

    repo = LocalProfileRepository(db)
    active = await repo.get_active_session()
    return active.profile_uuid if active else None


async def _get_or_create_player(db: AsyncSession, nesys_id: str) -> Player:
    """Get existing player by nesys_id or create with private-server defaults."""
    result = await db.execute(
        select(Player).where(Player.nesys_id == nesys_id)
    )
    player = result.scalar_one_or_none()
    if player is not None:
        return player

    player = Player(nesys_id=nesys_id)
    db.add(player)
    await db.flush()
    await db.commit()

    result2 = await db.execute(
        select(Player).where(Player.nesys_id == nesys_id)
    )
    player = result2.scalar_one()
    logger.info("Created new player for nesys_id=%s player_id=%d", nesys_id, player.player_id)
    return player


def _player_to_profile_dict(p: Player) -> dict[str, Any]:
    """Convert Player model to game-accepted profile response dict."""
    return {
        "player_id": p.player_id,
        "nesys_id": p.nesys_id,
        "player_name": p.player_name,
        "rank_id": p.rank_id,
        "rank_id_2on2": p.rank_id_2on2,
        "title_id": p.title_id,
        "title_id_2on2": p.title_id_2on2,
        "buddy_id": p.buddy_id,
        "buddy_intimacy": p.buddy_intimacy,
        "line_color_id": p.line_color_id,
        "ranking_pref_name": p.ranking_pref_name,
        "last_ranking_pref_name": p.last_ranking_pref_name,
        "match_mode_id": p.match_mode_id,
        "violation_point": p.violation_point,
        "emblem_id": p.emblem_id,
        "line_color_id_2on2": p.line_color_id_2on2,
        "emblem_id_2on2": p.emblem_id_2on2,
        "birth_day": p.birth_day,
        "birth_month": p.birth_month,
        "mecha_set_id": p.mecha_set_id,
        "side_weapon_id": p.side_weapon_id,
        "mecha_preset_id": p.mecha_preset_id,
        "rank_point": p.rank_point,
        "max_rank_id": p.max_rank_id,
        "rank_point_2on2": p.rank_point_2on2,
        "max_rank_id_2on2": p.max_rank_id_2on2,
        "same_day_login_count": 0,
        "total_login_days": 0,
        "consecutive_login_days": 0,
        "progresses": [],
        "last_pref_ranking_order_id": 0,
        "pref_ranking_top_player_count": 0,
        "official_player_type_id": 0,
    }


@router.post("/profile/load", response_model=None)
async def profile_load(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> dict[str, Any] | JSONResponse:
    response.headers["x-galaxy-api"] = "*/*"
    if x_galaxy_api_id:
        response.headers["x-galaxy-api-id"] = x_galaxy_api_id

    body = await request.json()
    nesys_id = body.get("nesys_id")
    if not nesys_id:
        return _ok(result=0)

    profile_uuid = await _get_active_profile_uuid(db)

    try:
        player = await _get_or_create_player(db, str(nesys_id))
        resp_payload = _player_to_profile_dict(player)
        await capture_request_metadata(request, "/player/profile/load", 200, profile_uuid)
        return resp_payload
    except Exception as exc:
        logger.warning("profile/load DB error: %s", exc)
        err_resp = _not_implemented("/player/profile/load", _galaxy_headers(x_galaxy_api_id))
        await capture_request_metadata(request, "/player/profile/load", err_resp.status_code, profile_uuid)
        return err_resp


@router.post("/login")
async def player_login(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> dict[str, Any]:
    response.headers["x-galaxy-api"] = "*/*"
    if x_galaxy_api_id:
        response.headers["x-galaxy-api-id"] = x_galaxy_api_id

    body = await request.json()
    player_id = body.get("player_id")
    logger.info("Player login: %s", player_id)

    try:
        await db.execute(
            text("INSERT INTO player_logins (player_id, ip_addr, ts_when) VALUES (:pid, '127.0.0.1', :now)"),
            {"pid": player_id, "now": datetime.now(timezone.utc)},
        )
        await db.commit()
    except Exception as exc:
        logger.warning("player/login DB insert failed: %s", exc)

    return _ok(
        player_id=player_id or "",
        progresses=[],
        greeting_ids=[1],
        battle_count=0,
        same_day_login_count=1,
        total_login_days=1,
        consecutive_login_days=1,
        burst_match=False,
        next_burst_begin="",
        next_burst_end="",
        open_boss_matches=[],
        next_boss_matches=[],
    )


@router.post("/login_bonus")
async def player_login_bonus(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/player/login_bonus", headers)
    return JSONResponse(
        content={"result": 1, "login_bonuses": [], "update_items": {}}, headers=headers
    )


@router.post("/logout")
async def player_logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    profile_uuid = await _get_active_profile_uuid(db)
    resp = _not_implemented("/player/logout", headers)
    await capture_request_metadata(request, "/player/logout", resp.status_code, profile_uuid)
    return resp


@router.post("/register")
async def player_register(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> dict[str, Any]:
    response.headers["x-galaxy-api"] = "*/*"
    if x_galaxy_api_id:
        response.headers["x-galaxy-api-id"] = x_galaxy_api_id

    body = await request.json()
    nesys_id = body.get("nesys_id", "")
    name = body.get("name", "")

    profile_uuid = await _get_active_profile_uuid(db)

    try:
        player = await _get_or_create_player(db, str(nesys_id))
        if name:
            await db.execute(
                text("UPDATE player SET player_name = :name WHERE player_id = :pid"),
                {"name": name, "pid": player.player_id},
            )
            await db.commit()
        resp = _ok(player_id=player.player_id)
        await capture_request_metadata(request, "/player/register", 200, profile_uuid)
        return resp
    except Exception as exc:
        logger.warning("player/register DB error: %s", exc)
        resp = _ok()
        await capture_request_metadata(request, "/player/register", 200, profile_uuid)
        return resp


@router.post("/{path:path}")
async def player_fallback(
    path: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    profile_uuid = await _get_active_profile_uuid(db)
    endpoint = f"/player/{path}"
    logger.debug("Unimplemented player endpoint: %s", endpoint)
    if settings.legacy_compatibility_mode:
        resp = JSONResponse(content=_ok(), headers=headers)
    else:
        resp = _not_implemented(endpoint, headers)
    await capture_request_metadata(request, endpoint, resp.status_code, profile_uuid)
    return resp
