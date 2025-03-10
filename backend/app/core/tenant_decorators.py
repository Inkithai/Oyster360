"""
Tenant-Aware Decorators
Automatically inject organization context into services
"""
from functools import wraps
from fastapi import HTTPException, Depends
from app.core.dependencies import get_current_user
from app.models.user import User

def require_organization(func):
    """
    Decorator to ensure user has an active organization
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user or not current_user.current_organization_id:
            raise HTTPException(
                status_code=403,
                detail="Active organization required. Please switch to an organization."
            )
        return await func(*args, **kwargs)
    return wrapper

def get_organization_id(current_user: User = Depends(get_current_user)) -> int:
    """Dependency to get current user's organization"""
    if not current_user.current_organization_id:
        raise HTTPException(
            status_code=403,
            detail="No active organization. Please switch to an organization."
        )
    return current_user.current_organization_id