"""Tests for the Redis-backed sliding-window limiter."""
from unittest.mock import AsyncMock

from app.core.rate_limit import RedisRateLimiter


def test_blocks_request_after_window_is_full():
    import asyncio
    limiter = RedisRateLimiter(max_requests=2)
    limiter.client.eval = AsyncMock(side_effect=[1, 1, 0])

    assert asyncio.run(limiter.allowed("1.2.3.4"))
    assert asyncio.run(limiter.allowed("1.2.3.4"))
    assert not asyncio.run(limiter.allowed("1.2.3.4"))
    assert limiter.client.eval.await_count == 3


def test_redis_script_uses_isolated_client_key():
    import asyncio
    limiter = RedisRateLimiter(max_requests=1)
    limiter.client.eval = AsyncMock(return_value=1)

    asyncio.run(limiter.allowed("10.0.0.1"))
    asyncio.run(limiter.allowed("10.0.0.2"))

    keys = [call.args[2] for call in limiter.client.eval.await_args_list]
    assert keys == ["oyster360:rate-limit:10.0.0.1", "oyster360:rate-limit:10.0.0.2"]
