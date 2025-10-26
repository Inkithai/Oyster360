"""Dependencies for resolving and enforcing the active organization."""

from fastapi import Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.models.user import User


def get_current_organization(current_user: User = Depends(get_current_user)) -> int:
    """Return the authenticated user's active organization.

    Tenant-scoped routes must never silently fall back to a shared organization,
    because doing so can expose another tenant's records.
    """
    if current_user.current_organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="An active organization is required",
        )
    return current_user.current_organization_id


def require_organization_access(
    organization_id: int,
    current_org: int = Depends(get_current_organization),
) -> int:
    if organization_id != current_org:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization",
        )
    return organization_id
