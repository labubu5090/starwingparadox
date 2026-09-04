"""Ranking endpoints (POST /ranking/*)."""

import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, Header, Request, Response
from fastapi.responses import JSONResponse

from app.config import settings

router = APIRouter(tags=["ranking"], prefix="/ranking")
logger = logging.getLogger(__name__)

def _fixed_term() -> dict[str, str]:
    return {"from_at": "2018-11-01 09:00:00", "to_at": "2038-12-31 09:00:00"}


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


async def _read_json(request: Request) -> dict[str, Any]:
    """Read request JSON defensively. Returns {} for empty/non-JSON bodies."""
    try:
        body = await request.body()
    except Exception:
        return {}
    if not body:
        return {}
    try:
        data = json.loads(body)
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        logger.warning("Non-JSON body for %s: %r", request.url.path, body[:256])
        return {}


@router.post("/national")
async def ranking_national(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/ranking/national", headers)
    return JSONResponse(
        content={
            "updated_at": "2018-11-01 09:00:00",
            "fixed_term": _fixed_term(),
            "records": [],
        },
        headers=headers,
    )


@router.post("/location")
async def ranking_location(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/ranking/location", headers)
    return JSONResponse(
        content={
            "updated_at": "2018-11-01 09:00:00",
            "fixed_term": _fixed_term(),
            "location_name": "バイキング",
            "records": [],
        },
        headers=headers,
    )


@router.post("/prefecture")
async def ranking_prefecture(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/ranking/prefecture", headers)
    return JSONResponse(
        content={
            "updated_at": "2018-11-01 09:00:00",
            "fixed_term": _fixed_term(),
            "pref_name": "東京都",
            "records": [],
        },
        headers=headers,
    )


@router.post("/event")
async def ranking_event(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/ranking/event", headers)
    return JSONResponse(
        content={"updated_at": "", "fixed_term": {"from_at": "", "to_at": ""}, "records": []},
        headers=headers,
    )


@router.post("/weapon")
async def ranking_weapon(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/ranking/weapon", headers)
    body = await _read_json(request)
    role_id = body.get("role_id", 1)
    return JSONResponse(
        content={
            "updated_at": "2018-11-01 09:00:00",
            "fixed_term": _fixed_term(),
            "role_id": role_id,
            "records": [],
        },
        headers=headers,
    )


@router.post("/{path:path}")
async def ranking_fallback(
    path: str,
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    logger.debug("Unimplemented ranking endpoint: /ranking/%s", path)
    if not settings.legacy_compatibility_mode:
        return _not_implemented(f"/ranking/{path}", headers)
    return JSONResponse(
        content={
            "updated_at": "2018-11-01 09:00:00",
            "fixed_term": _fixed_term(),
            "records": [],
        },
        headers=headers,
    )
