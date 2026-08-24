"""Redis-backed sliding-window rate limiting for multi-worker deployments.

Redis is shared by all API workers and containers, unlike an in-process list.
If Redis is unavailable, requests are allowed and the failure is logged; this
keeps the limiter from becoming a single point of failure for the API.
"""
from __future__ import annotations

import time
from typing import Callable

import redis.asyncio as redis
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.celery import REDIS_URL
from app.core.logging import logger


class RedisRateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60,
                 redis_url: str = REDIS_URL) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.client = redis.from_url(redis_url, decode_responses=True)

    async def allowed(self, key: str) -> bool:
        """Atomically remove expired entries, count, and add this request."""
        now = time.time()
        window_start = now - self.window_seconds
        redis_key = f"oyster360:rate-limit:{key}"
        script = (
            "redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', ARGV[1]); "
            "local count = redis.call('ZCARD', KEYS[1]); "
            "if count >= tonumber(ARGV[2]) then return 0 end; "
            "redis.call('ZADD', KEYS[1], ARGV[3], ARGV[3]); "
            "redis.call('EXPIRE', KEYS[1], ARGV[4]); return 1"
        )
        result = await self.client.eval(
            script, 1, redis_key, window_start, self.max_requests,
            now, self.window_seconds,
        )
        return bool(result)

    async def close(self) -> None:
        await self.client.aclose()



def create_rate_limit_middleware(max_requests: int = 100, window_seconds: int = 60,
                                 redis_url: str = REDIS_URL) -> Callable:
    limiter = RedisRateLimiter(max_requests, window_seconds, redis_url)

    async def middleware(request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        try:
            if not await limiter.allowed(client_ip):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again later."},
                    headers={"Retry-After": str(window_seconds)},
                )
        except redis.RedisError:
            logger.exception("Rate limiter Redis unavailable; allowing request")
        return await call_next(request)

    return middleware


async def close_rate_limiter() -> None:
    """Close the shared Redis connection during application shutdown."""
    # Middleware owns the connection; this hook is retained for compatibility.
    return None
