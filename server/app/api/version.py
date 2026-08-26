"""Version negotiation endpoint (POST /version)."""

from typing import Any

from fastapi import APIRouter, Header, Request, Response

from app.config import settings

router = APIRouter(tags=["version"])


@router.post("/version")
async def version_check(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> dict[str, Any]:
    response.headers["x-galaxy-api"] = "*/*"
    if x_galaxy_api_id:
        response.headers["x-galaxy-api-id"] = x_galaxy_api_id
    return {
        "client_version": str(settings.version_main),
        "data_version": str(settings.version_data),
        "stage_ids": [],
    }
