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
    """Extract organization_id from request state (set by middleware)"""
    return getattr(request.state, 'organization_id', None) or 1  # Default to 1 for demo