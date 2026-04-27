import json
import time
from collections import defaultdict, deque
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from config.settings import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

EXCLUDED_PATHS = {"/health"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window per-IP rate limiter."""

    def __init__(self, app, requests: int = RATE_LIMIT_REQUESTS, window: int = RATE_LIMIT_WINDOW):
        super().__init__(app)
        self._requests = requests
        self._window = window
        self._clients: dict[str, deque] = defaultdict(deque)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        ip = self._get_client_ip(request)
        now = time.time()
        window_start = now - self._window

        timestamps = self._clients[ip]
        # Purge timestamps outside the current window
        while timestamps and timestamps[0] < window_start:
            timestamps.popleft()

        if len(timestamps) >= self._requests:
            retry_after = int(self._window - (now - timestamps[0])) + 1
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "detail": f"Rate limit of {self._requests} requests per {self._window}s exceeded.",
                    "timestamp": str(now),
                },
                headers={"Retry-After": str(retry_after)},
            )

        timestamps.append(now)
        return await call_next(request)
