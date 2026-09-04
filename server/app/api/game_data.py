"""Game data endpoints (POST /game_data/*) with request capture."""

import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.capture.request_capture import capture_request_metadata
from app.config import settings
from app.dependencies import get_db_session

router = APIRouter(tags=["game_data"], prefix="/game_data")
logger = logging.getLogger(__name__)


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


def _safe_json_list(raw: Any) -> list:
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []
    if isinstance(raw, list):
        return raw
    return []


@router.post("/load")
async def game_data_load(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    profile_uuid = await _get_active_profile_uuid(db)

    try:
        body = await request.json()
        player_id = body.get("player_id")
        if not player_id:
            resp = JSONResponse(content={"player": {}, "buddies": [], "progresses": [], "options": [], "missions": [], "buddy_skills": [], "buddy_win_poses": [], "emblems": [], "emblem_parts": [], "titles": [], "line_colors": [], "mecha_sets": [], "mecha_set_parts": [], "mecha_colors": [], "weapon_set": [], "weapon_set_slots": [], "side_weapons": [], "violation_point": 0, "winning_streaks_2on2": 1}, headers=headers)
            await capture_request_metadata(request, "/game_data/load", 200, profile_uuid)
            return resp

        from app.db.models.player import Player
        from app.db.repositories.game_data_repository import GameDataRepository
        from sqlalchemy import select

        result = await db.execute(select(Player).where(Player.player_id == player_id))
        player = result.scalar_one_or_none()
        if not player:
            resp = JSONResponse(content={"player": {}, "buddies": [], "progresses": [], "options": [], "missions": []}, headers=headers)
            await capture_request_metadata(request, "/game_data/load", 200, profile_uuid)
            return resp

        repo = GameDataRepository(db)

        player_dict = {
            "player_id": player.player_id,
            "nesys_id": player.nesys_id,
            "player_name": player.player_name,
            "rank_id": player.rank_id,
            "rank_id_2on2": player.rank_id_2on2,
            "title_id": player.title_id,
            "title_id_2on2": player.title_id_2on2,
            "buddy_id": player.buddy_id,
            "buddy_intimacy": player.buddy_intimacy,
            "line_color_id": player.line_color_id,
            "ranking_pref_name": player.ranking_pref_name or "",
            "last_ranking_pref_name": player.last_ranking_pref_name or "",
            "match_mode_id": player.match_mode_id,
            "violation_point": player.violation_point,
            "emblem_id": player.emblem_id,
            "line_color_id_2on2": player.line_color_id_2on2,
            "emblem_id_2on2": player.emblem_id_2on2,
            "birth_day": player.birth_day,
            "birth_month": player.birth_month,
            "mecha_set_id": player.mecha_set_id,
            "side_weapon_id": player.side_weapon_id,
            "mecha_preset_id": player.mecha_preset_id,
            "rank_point": player.rank_point,
            "max_rank_id": player.max_rank_id,
            "rank_point_2on2": player.rank_point_2on2,
            "max_rank_id_2on2": player.max_rank_id_2on2,
            "same_day_login_count": 1,
            "total_login_days": 1,
            "consecutive_login_days": 1,
        }

        buddies_raw = await repo.get_buddies(player_id)
        buddies = [{"buddy_id": b.buddy_id, "buddy_key": b.buddy_key, "buddy_value": b.buddy_value} for b in buddies_raw]

        progresses_raw = await repo.get_progress(player_id)
        progresses = [{"progress_key": p.progress_key, "status": p.status} for p in progresses_raw]

        options_raw = await repo.get_options(player_id)
        options = [{"option_key": o.option_key, "value_num": o.value_num} for o in options_raw]

        missions_raw = await repo.get_missions(player_id)
        missions = [{"mission_id": m.mission_id, "clear_count": m.clear_count, "clear_num": m.clear_num, "status": m.status, "mission_status": m.mission_status} for m in missions_raw]

        buddy_win_poses_raw = await repo.get_buddy_win_poses(player_id)
        buddy_win_poses = [{"buddy_id": p.buddy_id, "win_pose_id": p.win_pose_id, "status": p.status} for p in buddy_win_poses_raw]

        emblems_raw = await repo.get_emblems(player_id)
        emblems = [{"emblem_id": e.emblem_id, "outline": e.outline, "main_design": e.main_design, "sub_design": e.sub_design} for e in emblems_raw]

        emblem_parts_raw = await repo.get_emblem_parts(player_id)
        emblem_parts = [{"part_id": p.part_id, "status": p.status} for p in emblem_parts_raw]

        titles_raw = await repo.get_titles(player_id)
        titles = [{"title_id": t.title_id, "status": t.status} for t in titles_raw]

        line_colors_raw = await repo.get_line_colors(player_id)
        line_colors = [{"line_color_id": lc.line_color_id, "status": lc.status} for lc in line_colors_raw]

        mecha_sets_raw = await repo.get_mecha_sets(player_id)
        mecha_sets = []
        for ms in mecha_sets_raw:
            parts_raw = await repo.get_mecha_set_parts(player_id, ms.mecha_set_id)
            mecha_sets.append({
                "mecha_set_id": ms.mecha_set_id,
                "mecha_setbonus_id": ms.mecha_setbonus_id,
                "weapon_set_id": ms.weapon_set_id,
                "parts": [{"part_id": p.part_id, "mecha_id": p.mecha_id, "design_id": p.design_id, "color_id": p.color_id} for p in parts_raw],
            })

        mecha_colors_raw = await repo.get_mecha_colors(player_id)
        mecha_colors = [{"mecha_color_id": mc.mecha_color_id, "status": mc.status} for mc in mecha_colors_raw]

        weapon_sets_raw = await repo.get_weapon_sets(player_id)
        weapon_set = [{"weapon_set_id": ws.weapon_set_id, "use_count": ws.use_count, "use_time": ws.use_time, "status": ws.status} for ws in weapon_sets_raw]

        weapon_set_slots_raw: list = []
        for ws in weapon_sets_raw:
            slots = await repo.get_weapon_set_slots(player_id, ws.weapon_set_id)
            weapon_set_slots_raw.extend(slots)
        weapon_set_slots = [{"weapon_set_id": s.weapon_set_id, "slot_id": s.slot_id, "weapon_id": s.weapon_id, "use_count": s.use_count, "use_time": s.use_time} for s in weapon_set_slots_raw]

        side_weapons_raw = await repo.get_side_weapons(player_id)
        side_weapons = [{"side_weapon_id": sw.side_weapon_id, "use_count": sw.use_count, "use_time": sw.use_time, "status": sw.status} for sw in side_weapons_raw]

        game_data = {
            "player": player_dict,
            "buddies": buddies,
            "progresses": progresses,
            "options": options,
            "missions": missions,
            "buddy_skills": [],
            "buddy_win_poses": buddy_win_poses,
            "emblems": emblems,
            "emblem_parts": emblem_parts,
            "titles": titles,
            "line_colors": line_colors,
            "mecha_sets": mecha_sets,
            "mecha_set_parts": [],
            "mecha_colors": mecha_colors,
            "weapon_set": weapon_set,
            "weapon_set_slots": weapon_set_slots,
            "side_weapons": side_weapons,
            "violation_point": player.violation_point,
            "winning_streaks_2on2": 1,
        }

        resp = JSONResponse(content=game_data, headers=headers)
        await capture_request_metadata(request, "/game_data/load", 200, profile_uuid)
        return resp
    except Exception as exc:
        logger.warning("game_data/load error: %s", exc)
        resp = _not_implemented("/game_data/load", headers)
        await capture_request_metadata(request, "/game_data/load", resp.status_code, profile_uuid)
        return resp


@router.post("/load/mission")
async def game_data_load_mission(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    profile_uuid = await _get_active_profile_uuid(db)

    try:
        body = await request.json()
        player_id = body.get("player_id")
        if not player_id:
            resp = JSONResponse(content={"missions": []}, headers=headers)
            await capture_request_metadata(request, "/game_data/load/mission", 200, profile_uuid)
            return resp

        from app.db.repositories.game_data_repository import GameDataRepository
        repo = GameDataRepository(db)
        missions_raw = await repo.get_missions(player_id)
        missions = [{"mission_id": m.mission_id, "clear_count": m.clear_count, "clear_num": m.clear_num, "status": m.status, "mission_status": m.mission_status} for m in missions_raw]

        resp = JSONResponse(content={"missions": missions}, headers=headers)
        await capture_request_metadata(request, "/game_data/load/mission", 200, profile_uuid)
        return resp
    except Exception as exc:
        logger.warning("game_data/load/mission error: %s", exc)
        resp = JSONResponse(content={"missions": []}, headers=headers)
        await capture_request_metadata(request, "/game_data/load/mission", 200, profile_uuid)
        return resp


@router.post("/save")
async def game_data_save(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    profile_uuid = await _get_active_profile_uuid(db)

    try:
        body = await request.json()
        player_id = body.get("player_id")
        if not player_id:
            resp = JSONResponse(content={"result": 1, "missions": []}, headers=headers)
            await capture_request_metadata(request, "/game_data/save", 200, profile_uuid)
            return resp

        from app.db.repositories.game_data_repository import GameDataRepository
        repo = GameDataRepository(db)

        for b in _safe_json_list(body.get("buddies")):
            await repo.upsert_buddy(player_id, b.get("buddy_id", 0), b.get("buddy_key", ""), b.get("buddy_value", "0"))

        for p in _safe_json_list(body.get("progresses")):
            await repo.upsert_progress(player_id, p.get("progress_key", ""), p.get("status", 0))

        for o in _safe_json_list(body.get("options")):
            await repo.upsert_option(player_id, o.get("option_key", ""), o.get("value_num", 0))

        for m in _safe_json_list(body.get("missions")):
            await repo.upsert_mission(player_id, m.get("mission_id", 0), m.get("clear_count", 0), m.get("clear_num", 0), m.get("status", 0), m.get("mission_status", 0))

        for t in _safe_json_list(body.get("titles")):
            await repo.upsert_title(player_id, t.get("title_id", 0), t.get("status", 0))

        for ep in _safe_json_list(body.get("emblem_parts")):
            await repo.upsert_emblem_part(player_id, ep.get("part_id", 0), ep.get("status", 0))

        for lc in _safe_json_list(body.get("line_colors")):
            await repo.upsert_line_color(player_id, lc.get("line_color_id", 0), lc.get("status", 0))

        for mc in _safe_json_list(body.get("mecha_colors")):
            await repo.upsert_mecha_color(player_id, mc.get("mecha_color_id", 0), mc.get("status", 0))

        for bwp in _safe_json_list(body.get("buddy_win_poses")):
            await repo.upsert_buddy_win_pose(player_id, bwp.get("buddy_id", 0), bwp.get("win_pose_id", 0), bwp.get("status", 0))

        for sw in _safe_json_list(body.get("side_weapons")):
            await repo.upsert_side_weapon(player_id, sw.get("side_weapon_id", 0), sw.get("use_count", 0), sw.get("use_time", 0), sw.get("status", 0))

        for ws in _safe_json_list(body.get("weapon_set")):
            await repo.upsert_weapon_set(player_id, ws.get("weapon_set_id", 0), ws.get("use_count", 0), ws.get("use_time", 0), ws.get("status", 0))

        for wss in _safe_json_list(body.get("weapon_set_slots")):
            await repo.upsert_weapon_set_slot(player_id, wss.get("weapon_set_id", 0), wss.get("slot_id", 0), wss.get("weapon_id", 0), wss.get("use_count", 0), wss.get("use_time", 0))

        for ms in _safe_json_list(body.get("mecha_set_parts")):
            await repo.upsert_mecha_set_part(player_id, ms.get("mecha_set_id", 0), ms.get("part_id", 0), ms.get("mecha_id", 0), ms.get("design_id", 0), ms.get("color_id", 0))

        from sqlalchemy import text
        for field in ["rank_id", "rank_id_2on2", "title_id", "title_id_2on2", "buddy_id", "buddy_intimacy", "line_color_id", "emblem_id", "line_color_id_2on2", "emblem_id_2on2", "mecha_set_id", "side_weapon_id", "mecha_preset_id", "rank_point", "max_rank_id", "rank_point_2on2", "max_rank_id_2on2", "violation_point"]:
            if field in body:
                await db.execute(text(f"UPDATE player SET {field} = :val WHERE player_id = :pid"), {"val": body[field], "pid": player_id})

        await db.commit()

        missions_raw = await repo.get_missions(player_id)
        missions = [{"mission_id": m.mission_id, "clear_count": m.clear_count, "clear_num": m.clear_num, "status": m.status, "mission_status": m.mission_status} for m in missions_raw]

        resp = JSONResponse(content={"result": 1, "missions": missions}, headers=headers)
        await capture_request_metadata(request, "/game_data/save", 200, profile_uuid)
        return resp
    except Exception as exc:
        logger.warning("game_data/save error: %s", exc)
        resp = JSONResponse(content={"result": 1, "missions": []}, headers=headers)
        await capture_request_metadata(request, "/game_data/save", 200, profile_uuid)
        return resp


@router.post("/{path:path}")
async def game_data_fallback(
    path: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    profile_uuid = await _get_active_profile_uuid(db)
    endpoint = f"/game_data/{path}"
    logger.debug("Unimplemented game_data endpoint: %s", endpoint)
    if settings.legacy_compatibility_mode:
        resp = JSONResponse(content={"result": 1}, headers=headers)
    else:
        resp = _not_implemented(endpoint, headers)
    await capture_request_metadata(request, endpoint, resp.status_code, profile_uuid)
    return resp
