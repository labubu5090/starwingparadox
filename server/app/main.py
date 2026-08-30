"""Starwing Paradox server – FastAPI application entry point."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.battle import router as battle_router
from app.api.credit import router as credit_router
from app.api.game_data import router as game_data_router
from app.api.health import router as health_router
from app.api.local_profile import router as local_profile_router
from app.api.matching import router as matching_router
from app.api.mission import router as mission_router
from app.api.player import router as player_router
from app.api.ranking import router as ranking_router
from app.api.resource import router as resource_router
from app.api.tutorial import router as tutorial_router
from app.api.version import router as version_router
from app.config import settings
from app.logging_config import setup_logging
from app.middleware.live_capture import LiveCaptureMiddleware
from app.middleware.protocol_logging import ProtocolLoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging(level=settings.log_level, json_format=settings.app_env == "production")
    logger.info("Starting Starwing Paradox server env=%s", settings.app_env)

    from app.dependencies import dispose_database, init_database

    await init_database()
    yield
    logger.info("Shutting down – disposing DB pool")
    await dispose_database()


app = FastAPI(
    title="Starwing Paradox Server",
    version=f"{settings.version_main}.{settings.version_data}",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LiveCaptureMiddleware)
app.add_middleware(ProtocolLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

app.include_router(health_router)
app.include_router(version_router)
app.include_router(resource_router)
app.include_router(player_router)
app.include_router(game_data_router)
app.include_router(matching_router)
app.include_router(ranking_router)
app.include_router(mission_router)
app.include_router(credit_router)
app.include_router(tutorial_router)
app.include_router(battle_router)
app.include_router(local_profile_router)
