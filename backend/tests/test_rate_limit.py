"""Tests for the Redis-backed sliding-window limiter."""
import asyncio

import pytest
from unittest.mock import AsyncMock

import redis

from app.core.rate_limit import RedisRateLimiter, create_rate_limit_middleware


def test_blocks_request_after_window_is_full():
    limiter = RedisRateLimiter(max_requests=2)
    limiter.client.eval = AsyncMock(side_effect=[1, 1, 0])

    assert asyncio.run(limiter.allowed("1.2.3.4"))
    assert asyncio.run(limiter.allowed("1.2.3.4"))
    assert not asyncio.run(limiter.allowed("1.2.3.4"))
    assert limiter.client.eval.await_count == 3


def test_redis_script_uses_isolated_client_key():
    limiter = RedisRateLimiter(max_requests=1)
    limiter.client.eval = AsyncMock(return_value=1)

    asyncio.run(limiter.allowed("10.0.0.1"))
    asyncio.run(limiter.allowed("10.0.0.2"))

    keys = [call.args[2] for call in limiter.client.eval.await_args_list]
    assert keys == ["oyster360:rate-limit:10.0.0.1", "oyster360:rate-limit:10.0.0.2"]


class _FakeRequest:
    """Minimal stand-in for starlette.requests.Request used by the middleware."""

    def __init__(self, host: str = "1.2.3.4") -> None:
        self.client = type("Client", (), {"host": host})()


@pytest.mark.parametrize(
    "raised",
    [
        redis.ConnectionError("boom"),
        # Mirrors the failure seen with FastAPI's TestClient: a pooled
        # asyncio Redis connection created on one event loop is reused by a
        # request that runs on a different loop (e.g. following a 307
        # redirect), and redis-py's transport surfaces that as a bare
        # RuntimeError rather than a redis.RedisError subclass.
        RuntimeError("Event loop is closed"),
        OSError("Connection reset by peer"),
    ],
)
def test_middleware_fails_open_when_redis_is_unreachable(raised):
    middleware = create_rate_limit_middleware(max_requests=1, window_seconds=60)

    async def call_next(request):
        return "downstream-response"

    async def broken_allowed(self, key):
        raise raised

    original_allowed = RedisRateLimiter.allowed
    RedisRateLimiter.allowed = broken_allowed
    try:
        response = asyncio.run(middleware(_FakeRequest(), call_next))
    finally:
        RedisRateLimiter.allowed = original_allowed

    assert response == "downstream-response"
