"""
Tenant Scope Helper
Automatically applies organization filtering
"""
from sqlalchemy.orm import Query
from fastapi import Request

def apply_tenant_filter(query: Query, model, organization_id: int):
    """
    Apply organization filter to queries.
    Assumes the model has an 'organization_id' column or belongs to an organization via relationship.
    """
    if hasattr(model, 'organization_id'):
        return query.filter(model.organization_id == organization_id)
    return query

def get_organization_id_from_request(request: Request) -> int:
    """Extract the organization ID set by the tenant middleware."""
    organization_id = getattr(request.state, "organization_id", None)
    if organization_id is None:
        raise ValueError("No active organization is available for this request")
    return organization_id