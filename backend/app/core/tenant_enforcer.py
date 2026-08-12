"""
Tenant Enforcer
Prevents unsafe tenant queries
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Type, Any

class TenantEnforcer:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def safe_get(self, model: Type[Any], id: int) -> Any:
        """Safely get a record with tenant verification"""
        if not hasattr(model, 'organization_id'):
            # Model doesn't support tenant isolation
            return self.db.query(model).filter(model.id == id).first()
        
        obj = self.db.query(model).filter(
            model.id == id,
            model.organization_id == self.organization_id
        ).first()
        
        if not obj:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found or access denied")
        return obj

    def safe_filter(self, model: Type[Any], **filters):
        """Apply tenant filtering automatically"""
        query = self.db.query(model)
        
        if hasattr(model, 'organization_id'):
            query = query.filter(model.organization_id == self.organization_id)
        
        for key, value in filters.items():
            query = query.filter(getattr(model, key) == value)
            
        return query

    def get_all(self, model: Type[Any]):
        """Return every record visible to the current organization."""
        return self.safe_filter(model).all()

    def safe_create(self, model: Type[Any], **kwargs) -> Any:
        """Automatically assign organization_id on creation"""
        if hasattr(model, 'organization_id'):
            kwargs['organization_id'] = self.organization_id
        
        obj = model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj