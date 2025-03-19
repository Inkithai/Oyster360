"""Tests for API pagination utilities (app.core.api_utils)."""
from datetime import datetime

from app.core.api_utils import PaginatedResponse, get_pagination_params, paginate
from app.models.recipe import Recipe


def test_get_pagination_params_returns_values():
    # Defaults are FastAPI Query objects resolved per-request; when called with
    # explicit values the function echoes them back as the dependency payload.
    params = get_pagination_params(page=3, page_size=50)
    assert params == {"page": 3, "page_size": 50}


def test_paginate_calculates_metadata(db_session):
    for i in range(5):
        db_session.add(Recipe(name=f"R{i}", organization_id=1, created_at=datetime.utcnow()))
    db_session.commit()

    query = db_session.query(Recipe)

    first = paginate(query, page=1, page_size=2)
    assert first["total"] == 5
    assert len(first["items"]) == 2
    assert first["page"] == 1
    assert first["page_size"] == 2
    assert first["has_next"] is True
    assert first["has_prev"] is False

    last = paginate(query, page=3, page_size=2)
    assert len(last["items"]) == 1
    assert last["has_next"] is False
    assert last["has_prev"] is True


def test_paginated_response_model():
    resp = PaginatedResponse(
        items=[1, 2], total=2, page=1, page_size=10, has_next=False, has_prev=False
    )
    assert resp.total == 2
    assert resp.has_next is False
