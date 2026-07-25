import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import settings


class TenantMiddleware(BaseHTTPMiddleware):
    """Expose the signed organization claim to request-aware services.

    Route dependencies still load the user and enforce the current organization;
    the middleware intentionally performs no database I/O.
    """

    async def dispatch(self, request: Request, call_next):
        request.state.organization_id = None

        auth_header = request.headers.get("Authorization", "")
        scheme, _, token = auth_header.partition(" ")
        if scheme.lower() == "bearer" and token:
            try:
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                )
                request.state.organization_id = payload.get("organization_id")
            except jwt.InvalidTokenError:
                # Authentication dependencies return the authoritative 401.
                pass

        return await call_next(request)
