from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.dependencies import get_current_user
from app.database.database import SessionLocal

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth endpoints
        if request.url.path.startswith("/api/auth"):
            return await call_next(request)
        
        try:
            # Get user from token
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return await call_next(request)
            
            token = auth_header.split(" ")[1]
            from jose import jwt
            from app.core.config import settings
            
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = int(payload.get("sub"))
            
            # Get user's current organization
            db = SessionLocal()
            from app.models.user import User
            user = db.query(User).filter(User.id == user_id).first()
            db.close()
            
            if user and user.current_organization_id:
                request.state.organization_id = user.current_organization_id
            else:
                request.state.organization_id = None
                
        except Exception:
            request.state.organization_id = None
            
        return await call_next(request)