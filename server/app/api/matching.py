"""Matching / lobby endpoints (POST /matching/*)."""

import logging
import random
import uuid
from typing import Any

from fastapi import APIRouter, Header, Request, Response
from fastapi.responses import JSONResponse

from app.config import settings

router = APIRouter(tags=["matching"], prefix="/matching")
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


@router.post("/server")
async def matching_server(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/matching/server", headers)
    matcher = f"{settings.matcher_hostname}:{settings.pb_port}"
    return JSONResponse(content={"ip_addr": matcher}, headers=headers)


@router.post("/match_id/generate")
async def match_id_generate(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/matching/match_id/generate", headers)
    match_id = random.randint(10000, 99999)
    return JSONResponse(content={"match_id": match_id}, headers=headers)


@router.post("/{path:path}")
async def matching_fallback(
    path: str,
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    logger.debug("Unimplemented matching endpoint: /matching/%s", path)
    if not settings.legacy_compatibility_mode:
        return _not_implemented(f"/matching/{path}", headers)
    return JSONResponse(content={}, headers=headers)
