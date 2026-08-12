"""
Multi-Tenant Support for Oyster360
"""
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user

def get_current_organization(
    current_user: User = Depends(get_current_user)
) -> int:
    """
    In production, this would extract organization from JWT or user settings.
    For now, returns a default organization for demo purposes.
    """
    # TODO: Implement real multi-tenant logic
    return 1  # Default organization for demo

def require_organization_access(
    organization_id: int,
    current_org: int = Depends(get_current_organization)
):
    if organization_id != current_org:
        raise HTTPException(status_code=403, detail="Access denied to this organization")
    return organization_id