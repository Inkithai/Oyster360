"""Tests for the in-memory rate limiter (app.core.rate_limit)."""
import pytest
from fastapi import HTTPException

from app.core import rate_limit


class _FakeRequest:
    def __init__(self, host="1.2.3.4"):
        # Mirror the attribute the decorator reads (request.client.host).
        self.client = type("C", (), {"host": host})()


@pytest.fixture(autouse=True)
def _reset_counts():
    rate_limit.request_counts.clear()
    yield
    rate_limit.request_counts.clear()


async def _handler(request):
    return "ok"


def test_allows_requests_under_limit():
    limiter = rate_limit.rate_limit(max_requests=3, window_seconds=60)(_handler)
    import asyncio
    for _ in range(3):
        assert asyncio.get_event_loop().run_until_complete(limiter(_FakeRequest())) == "ok"


def test_blocks_requests_over_limit():
    limiter = rate_limit.rate_limit(max_requests=2, window_seconds=60)(_handler)
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(limiter(_FakeRequest()))
    loop.run_until_complete(limiter(_FakeRequest()))
    with pytest.raises(HTTPException) as exc:
        loop.run_until_complete(limiter(_FakeRequest()))
    assert exc.value.status_code == 429


def test_rate_limit_is_per_client():
    limiter = rate_limit.rate_limit(max_requests=1, window_seconds=60)(_handler)
    import asyncio
    loop = asyncio.new_event_loop()
    loop.run_until_complete(limiter(_FakeRequest("10.0.0.1")))  # ok
    # Different client gets its own bucket.
    assert loop.run_until_complete(limiter(_FakeRequest("10.0.0.2"))) == "ok"


def test_middleware_allows_requests_under_budget():
    import asyncio

    async def call_next(_request):
        return "passed-through"

    rate_limit.request_counts.clear()
    limiter = rate_limit.rate_limit_middleware
    result = asyncio.new_event_loop().run_until_complete(limiter(_FakeRequest(), call_next))
    assert result == "passed-through"


def test_middleware_blocks_requests_over_budget():
    import asyncio

    async def call_next(_request):
        return "should-not-run"

    loop = asyncio.new_event_loop()
    rate_limit.request_counts.clear()
    # Saturate the shared bucket for this client up to the middleware budget.
    saturate_ip = "203.0.113.9"
    rate_limit.request_counts[saturate_ip] = [
        rate_limit.time.time() - 1
    ] * rate_limit.MIDDLEWARE_MAX_REQUESTS

    response = loop.run_until_complete(
        rate_limit.rate_limit_middleware(_FakeRequest(saturate_ip), call_next)
    )
    assert response.status_code == 429
    assert b"Too many requests" in response.body


def test_decorator_handles_missing_client():
    """Requests without client info are bucketed under 'unknown', not crashed."""
    import asyncio

    class _NoClientRequest:
        client = None

    limiter = rate_limit.rate_limit(max_requests=2, window_seconds=60)(_handler)
    rate_limit.request_counts.clear()
    loop = asyncio.new_event_loop()
    assert loop.run_until_complete(limiter(_NoClientRequest())) == "ok"
