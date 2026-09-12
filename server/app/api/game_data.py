"""Game data endpoints (POST /game_data/*) with request capture."""

import json
import logging
import uuid
from typing import Any
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.capture.request_capture import capture_request_metadata
from app.config import settings
from app.dependencies import get_db_session

router = APIRouter(tags=["game_data"], prefix="/game_data")
logger = logging.getLogger(__name__)


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
        body = await _parse_request_body(request)
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
        emblems = [{
            "emblem_id": e.emblem_id,
            "outline": {"part_id": e.outline_part_id, "offset": [e.outline_offset_x, e.outline_offset_y], "scale": [e.outline_scale_x, e.outline_scale_y], "angle": e.outline_angle},
            "main_design": {"part_id": e.main_design_part_id, "offset": [e.main_design_offset_x, e.main_design_offset_y], "scale": [e.main_design_scale_x, e.main_design_scale_y], "angle": e.main_design_angle},
            "sub_design": {"part_id": e.sub_design_part_id, "offset": [e.sub_design_offset_x, e.sub_design_offset_y], "scale": [e.sub_design_scale_x, e.sub_design_scale_y], "angle": e.sub_design_angle},
            "status": e.status,
            "editable": e.editable,
        } for e in emblems_raw]

        emblem_parts_raw = await repo.get_emblem_parts(player_id)
        emblem_parts = [{"part_id": p.part_id, "status": p.status} for p in emblem_parts_raw]

        titles_raw = await repo.get_titles(player_id)
        titles = [{"title_id": t.title_id, "status": t.status} for t in titles_raw]

        line_colors_raw = await repo.get_line_colors(player_id)
        line_colors = [{"line_color_id": lc.line_color_id, "status": lc.status} for lc in line_colors_raw]

        mecha_sets_raw = await repo.get_mecha_sets(player_id)
        mecha_sets = [
            {
                "mecha_set_id": ms.mecha_set_id,
                "mecha_setbonus_id": ms.mecha_setbonus_id,
                "weapon_set_id": ms.weapon_set_id,
                "is_decal": ms.is_decal,
                "favorite": ms.favorite,
                "use_count": ms.use_count,
                "use_time": ms.use_time,
                "status": ms.status,
                "win_count": ms.win_count,
                "winning_streaks": ms.winning_streaks,
            }
            for ms in mecha_sets_raw
        ]

        mecha_set_parts_raw = await repo.get_mecha_set_parts(player_id)
        mecha_set_parts = [
            {
                "mecha_set_id": p.mecha_set_id,
                "part_id": p.part_id,
                "mecha_id": p.mecha_id,
                "design_id": p.design_id,
                "color_id": p.color_id,
            }
            for p in mecha_set_parts_raw
        ]

        mecha_colors_raw = await repo.get_mecha_colors(player_id)
        mecha_colors = [{"mecha_color_id": mc.mecha_color_id, "status": mc.status} for mc in mecha_colors_raw]

        weapon_sets_raw = await repo.get_weapon_sets(player_id)
        weapon_set = [{"weapon_set_id": ws.weapon_set_id, "use_count": ws.use_count, "use_time": ws.use_time, "status": ws.status} for ws in weapon_sets_raw]

        weapon_set_slots_raw: list = []
        for ws in weapon_sets_raw:
            slots = await repo.get_weapon_set_slots(player_id, ws.weapon_set_id)
            weapon_set_slots_raw.extend(slots)
        weapon_set_slots = [{"weapon_set_id": s.weapon_set_id, "slot_id": s.slot_id + 1, "weapon_id": s.weapon_id, "use_count": s.use_count, "use_time": s.use_time} for s in weapon_set_slots_raw]

        side_weapons_raw = await repo.get_side_weapons(player_id)
        side_weapons = [{"side_weapon_id": sw.side_weapon_id, "use_count": sw.use_count, "use_time": sw.use_time, "status": sw.status} for sw in side_weapons_raw]

        # Client UPlayerProfileWork::ReceiveHttpGameDataLoadDelegate_UserCharCustom
        # fills MyPlayerProfile.UserCharCustom from the *mecha_presets* array, one
        # entry per preset (initialized from Pl001, then name/is_decal/setbonus
        # overwritten). SetPlParts -> GetEquipPlayerCustomizeProfileRobot then reads
        # UserCharCustom[RobotPresetNumber-1]; with an empty array the player mecha
        # spawns with no customize (SetPlParts error, camera lock). MechaSetID:
        # read-side picks PlayerData.MechaSetID when MechaSetInfoList is non-empty,
        # so seed mecha_presets from the equipped mecha set.
        equip_set_id = player.mecha_set_id
        equip_parts_raw = await repo.get_mecha_set_parts(player_id, equip_set_id)
        if not equip_parts_raw:
            equip_set_id = None
            for ms in mecha_sets_raw:
                if ms.status == 4:
                    cand = await repo.get_mecha_set_parts(player_id, ms.mecha_set_id)
                    if cand:
                        equip_set_id = ms.mecha_set_id
                        equip_parts_raw = cand
                        break

        mecha_set_bonus = 0
        for ms in mecha_sets_raw:
            if ms.mecha_set_id == equip_set_id:
                mecha_set_bonus = ms.mecha_setbonus_id or 0
                break

        if equip_set_id is not None:
            mecha_presets = [{
                "preset_id": 1,
                "name": "default",
                "is_decal": False,
                "mecha_setbonus_id": mecha_set_bonus,
            }]
            mecha_preset_parts = [{
                "preset_id": 1,
                "part_id": p.part_id,
                "mecha_id": p.mecha_id,
                "design_id": p.design_id,
                "color_id": p.color_id,
            } for p in sorted(equip_parts_raw, key=lambda x: x.part_id)]
        else:
            mecha_presets = []
            mecha_preset_parts = []

        # Client FCPP_HttpJsonSerialize reads role_id/preset_id from weapon_roles,
        # and GetWeaponPackSet (sub_142E6E040) requires FRoleData.RoleID(+8) in
        # {1,2,3,4} (mecha class) and joins role.PresetID(+12) with slot.PresetID(+8),
        # slot.SlotID(+12) in {1..4}, slot.WeaponID(+16).  Seed weapon_set_id encodes
        # class as the leading hundred: 100/200/300/400 -> classes 1..4.
        class_hundreds = []
        for ws in sorted(weapon_sets_raw, key=lambda w: w.weapon_set_id):
            h = ws.weapon_set_id // 100
            if ws.status == 4 and h not in class_hundreds:
                class_hundreds.append(h)
        hundred_class = {h: i + 1 for i, h in enumerate(class_hundreds[:4])}
        class_of_set = {}
        for ws in weapon_sets_raw:
            h = ws.weapon_set_id // 100
            if h in hundred_class:
                class_of_set[ws.weapon_set_id] = hundred_class[h]

        weapon_roles = []
        weapon_role_presets = []
        weapon_role_preset_slots = []
        for ws in sorted(weapon_sets_raw, key=lambda w: w.weapon_set_id):
            role_id = class_of_set.get(ws.weapon_set_id)
            if role_id is None:
                continue
            slots = sorted(
                (s for s in weapon_set_slots_raw if s.weapon_set_id == ws.weapon_set_id),
                key=lambda s: s.slot_id,
            )
            if not slots:
                continue
            weapon_roles.append({
                "role_id": role_id,
                "preset_id": ws.weapon_set_id,
                "weapon_id": slots[0].weapon_id,
                "main_id": 1,
                "sub_id": 0,
                "clear_status": 1,
                "color_id": 0,
                "use_count": ws.use_count,
                "login": 0,
                "use_time": ws.use_time,
                "favorite": 0,
                "status": 4,
            })
            weapon_role_presets.append({
                "role_id": role_id,
                "preset_id": ws.weapon_set_id,
                "name": "set_%d" % ws.weapon_set_id,
                "use_count": ws.use_count,
                "use_time": ws.use_time,
                "status": ws.status,
            })
            for s in slots:
                weapon_role_preset_slots.append({
                    "role_id": role_id,
                    "preset_id": ws.weapon_set_id,
                    "slot_id": s.slot_id + 1,
                    "weapon_id": s.weapon_id,
                    "use_count": s.use_count,
                    "use_time": s.use_time,
                })

        weapons_owned = {}
        for s in weapon_set_slots_raw:
            if s.weapon_id == 0:
                continue
            if s.weapon_id not in weapons_owned:
                weapons_owned[s.weapon_id] = {"weapon_id": s.weapon_id, "use_count": s.use_count, "use_time": s.use_time, "favorite": False, "status": 4}
        weapons = list(weapons_owned.values())

        # mecha_preset_id seeds CustomizePlayerProfile.RobotPresetNumber (1-based),
        # which SetPlParts -> GetEquipPlayerCustomizeProfileRobot uses as
        # UserCharCustom[preset-1]. A stale DB value of 0 (never saved a preset)
        # yields index -1 -> "FCharacterCustomize In PlayerProfile" error +
        # per-tick SetPlParts/NicePlay spam. Point it at the seeded preset.
        if not (1 <= (player.mecha_preset_id or 0) <= len(mecha_presets)):
            player_dict["mecha_preset_id"] = 1

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
            "mecha_set_parts": mecha_set_parts,
            "mechas": mecha_sets,
            "mecha_parts": mecha_set_parts,
            "mecha_presets": mecha_presets,
            "mecha_preset_parts": mecha_preset_parts,
            "weapon_roles": weapon_roles,
            "weapon_role_presets": weapon_role_presets,
            "weapon_role_preset_slots": weapon_role_preset_slots,
            "weapons": weapons,
            "mecha_colors": mecha_colors,
            "weapon_set": weapon_set,
            "weapon_set_slots": weapon_set_slots,
            "side_weapons": side_weapons,
            "symbol_chats": [],
            "symbol_chat_slots": [],
            "cockpit_items": [],
            "present_items": [],
            "greetings": [],
            "buddy_greetings": [],
            "game_moneys": [],
            "quests": [],
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
        body = await _parse_request_body(request)
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
        body = await _parse_request_body(request)
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
            mission_id = int(m.get("mission_id", 0))
            status = int(m.get("status", 0))
            mission_status = int(m.get("mission_status", 0))
            existing = await repo.get_mission(int(player_id), mission_id)
            if existing is not None and existing.mission_status == 400 and existing.status == 0:
                status = 0
                mission_status = 400
            await repo.upsert_mission(
                int(player_id),
                mission_id,
                int(m.get("clear_count", 0)),
                int(m.get("clear_num", 0)),
                status,
                mission_status,
            )

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
