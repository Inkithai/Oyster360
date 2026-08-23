"""
In-memory rate limiting.

Two complementary primitives live here:

- ``rate_limit``: a decorator for individual endpoints that need their own
  tighter budget (for example credential endpoints).
- ``rate_limit_middleware``: the application-wide per-client throttle used by
  ``app.main``.

Both share a sliding one-minute window keyed by client IP and are safe for
single-process deployments; production multi-replica setups should move the
store to Redis (see docs/ARCHITECTURE.md).
"""
import time
from collections import defaultdict
from typing import Callable, Dict

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse

# In-memory store (use Redis in production)
request_counts: Dict[str, list] = defaultdict(list)

# Application-wide middleware budget: requests per window per client.
MIDDLEWARE_MAX_REQUESTS = 100
MIDDLEWARE_WINDOW_SECONDS = 60


def _recent_timestamps(client_ip: str, now: float, window_seconds: int) -> list:
    """Return the still-recent slice of a client's request history."""
    request_counts[client_ip] = [
        t for t in request_counts[client_ip] if now - t < window_seconds
    ]
    return request_counts[client_ip]


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """Simple rate limiting decorator for individual endpoints."""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host if request.client else "unknown"
            current_time = time.time()

            recent = _recent_timestamps(client_ip, current_time, window_seconds)

            if len(recent) >= max_requests:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later."
                )

            request_counts[client_ip].append(current_time)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    """Throttle every incoming request per client IP (sliding window)."""
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()

    recent = _recent_timestamps(
        client_ip, current_time, MIDDLEWARE_WINDOW_SECONDS
    )

    if len(recent) >= MIDDLEWARE_MAX_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."}
        )

    request_counts[client_ip].append(current_time)
    return await call_next(request)


def reset_store() -> None:
    """Clear the shared store (used by tests to isolate cases)."""
    request_counts.clear()
