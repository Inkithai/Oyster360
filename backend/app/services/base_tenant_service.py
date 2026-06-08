"""
Base Tenant Service
Enforces organization isolation on all operations
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException

class TenantService:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _verify_ownership(self, model_instance):
        """Verify that a resource belongs to the current organization"""
        if hasattr(model_instance, 'organization_id'):
            if model_instance.organization_id != self.organization_id:
                raise HTTPException(
                    status_code=403, 
                    detail="You do not have access to this resource"
                )
        return True

    def filter_by_organization(self, query):
        """Apply organization filter to queries"""
        if hasattr(query.column_descriptions[0]['entity'], 'organization_id'):
            return query.filter(
                query.column_descriptions[0]['entity'].organization_id == self.organization_id
            )
        return query