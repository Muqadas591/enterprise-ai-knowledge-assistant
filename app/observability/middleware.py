import json
import logging
import threading
import time
from collections import defaultdict, deque
from uuid import uuid4

from fastapi import Request
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.security.jwt import decode_access_token

logger = logging.getLogger(__name__)


class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = request_id
        started = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "api_request %s",
                json.dumps(
                    {
                        "request_id": request_id,
                        "method": request.method,
                        "endpoint": request.url.path,
                        "status": 500,
                        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                    },
                    sort_keys=True,
                ),
            )
            raise

        response.headers["X-Request-ID"] = request_id
        logger.info(
            "api_request %s",
            json.dumps(
                {
                    "request_id": request_id,
                    "method": request.method,
                    "endpoint": request.url.path,
                    "status": response.status_code,
                    "user_id": getattr(request.state, "user_id", None),
                    "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                },
                sort_keys=True,
            ),
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    protected_prefixes = ("/api/v1/qa", "/api/v1/documents", "/api/v1/retrieval")

    def __init__(self, app):
        super().__init__(app)
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(self.protected_prefixes):
            key = self._client_key(request)
            now = time.monotonic()
            cutoff = now - settings.RATE_LIMIT_WINDOW_SECONDS
            with self._lock:
                timestamps = self._requests[key]
                while timestamps and timestamps[0] <= cutoff:
                    timestamps.popleft()
                if len(timestamps) >= settings.RATE_LIMIT_REQUESTS:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Rate limit exceeded."},
                        headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW_SECONDS)},
                    )
                timestamps.append(now)

        return await call_next(request)

    @staticmethod
    def _client_key(request: Request) -> str:
        authorization = request.headers.get("Authorization", "")
        if authorization.lower().startswith("bearer "):
            try:
                subject = decode_access_token(authorization[7:]).get("sub")
                if subject:
                    return f"user:{subject}"
            except (JWTError, ValueError, TypeError):
                pass
        return f"ip:{request.client.host if request.client else 'unknown'}"
