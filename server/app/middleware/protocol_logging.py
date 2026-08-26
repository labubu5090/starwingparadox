"""Middleware that logs basic request/response metrics."""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("protocol")


class ProtocolLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        client = request.client.host if request.client else "-"
        logger.info(
            "%s %s %s %d %.1fms",
            request.method,
            request.url.path,
            client,
            response.status_code,
            elapsed_ms,
        )
        return response
