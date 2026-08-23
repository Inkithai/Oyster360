"""
HTTP middleware shared by the application entrypoint.

Keeping request-scoped cross-cutting concerns (request IDs, security headers)
in one module leaves `app.main` focused on application wiring: routers,
exception handling, and operational endpoints.
"""
import time
import uuid

from fastapi import Request

from app.core.logging import logger

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'"
    ),
}


async def add_security_headers(request: Request, call_next):
    """Attach defensive browser headers to every response."""
    response = await call_next(request)
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response


async def add_request_id(request: Request, call_next):
    """Correlate every request/response pair with a unique request ID.

    The ID is exposed on the response (`X-Request-ID`), on `request.state`
    for handlers and log records, and in the structured access log line.
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    started_at = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
        },
    )
    return response
