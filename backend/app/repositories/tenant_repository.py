"""
Tenant Repository
Provides safe, tenant-isolated database operations
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Type, TypeVar, List, Optional

T = TypeVar('T')

class TenantRepository:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _filter_by_tenant(self, model: Type[T], query=None):
        """Apply organization filter"""
        if query is None:
            query = self.db.query(model)
        
        if hasattr(model, 'organization_id'):
            return query.filter(model.organization_id == self.organization_id)
        return query

    def get_all(self, model: Type[T]) -> List[T]:
        return self._filter_by_tenant(model).all()

    def get_by_id(self, model: Type[T], id: int) -> Optional[T]:
        obj = self._filter_by_tenant(model).filter(model.id == id).first()
        if obj is None:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        return obj

    def create(self, model: Type[T], **kwargs) -> T:
        # Automatically assign organization
        if hasattr(model, 'organization_id'):
            kwargs['organization_id'] = self.organization_id
        
        obj = model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, model: Type[T], id: int, **kwargs) -> T:
        obj = self.get_by_id(model, id)
        
        # Verify ownership before update
        if hasattr(obj, 'organization_id') and obj.organization_id != self.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this resource")
        
        for key, value in kwargs.items():
            setattr(obj, key, value)
        
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, model: Type[T], id: int) -> bool:
        obj = self.get_by_id(model, id)
        
        # Verify ownership before delete
        if hasattr(obj, 'organization_id') and obj.organization_id != self.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this resource")
        
        self.db.delete(obj)
        self.db.commit()
        return True