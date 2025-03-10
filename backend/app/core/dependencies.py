from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.database import get_db
from app.models.user import User, UserRole

security = HTTPBearer(auto_error=False)


def _authentication_error(detail: str = "Invalid token") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise _authentication_error("Authentication required")

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError, jwt.InvalidTokenError):
        raise _authentication_error()

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise _authentication_error("User not found")
    return user


def require_role(allowed_roles: list[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_checker


# Role shortcuts
admin_only = require_role([UserRole.ADMIN])
manager_only = require_role([UserRole.ADMIN, UserRole.FARM_MANAGER])
worker_access = require_role([UserRole.ADMIN, UserRole.FARM_MANAGER, UserRole.WORKER])
viewer_access = require_role(
    [UserRole.ADMIN, UserRole.FARM_MANAGER, UserRole.WORKER, UserRole.VIEWER]
)
