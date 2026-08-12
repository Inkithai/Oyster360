"""
Oyster360 API Utilities
Pagination, filtering, and response standards
"""
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel
from fastapi import Query

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool

def get_pagination_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    return {"page": page, "page_size": page_size}

def paginate(query, page: int, page_size: int) -> dict:
    """Apply pagination to SQLAlchemy query"""
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_next": page * page_size < total,
        "has_prev": page > 1
    }