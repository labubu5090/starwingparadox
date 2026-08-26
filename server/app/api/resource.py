"""Resource endpoint – serves c_resource.json (POST /resource)."""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Header, Request, Response

router = APIRouter(tags=["resource"])

RESOURCE_PATH = Path(__file__).resolve().parents[3] / "c_resource.json"


@router.post("/resource")
async def load_resource(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> dict[str, Any]:
    response.headers["x-galaxy-api"] = "*/*"
    if x_galaxy_api_id:
        response.headers["x-galaxy-api-id"] = x_galaxy_api_id

    if RESOURCE_PATH.exists():
        loaded: dict[str, Any] = json.loads(RESOURCE_PATH.read_text(encoding="utf-8"))
        return loaded
    return {}
