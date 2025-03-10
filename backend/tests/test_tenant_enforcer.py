"""Tests for the multi-tenant TenantEnforcer (app.core.tenant_enforcer)."""
from datetime import datetime

import pytest
from fastapi import HTTPException

from app.core.tenant_enforcer import TenantEnforcer
from app.models.recipe import Recipe


def _make_recipe(db, org_id, name):
    recipe = Recipe(name=name, organization_id=org_id, created_at=datetime.utcnow())
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


def test_safe_get_returns_owned_record(db_session):
    recipe = _make_recipe(db_session, org_id=10, name="Owned")
    enforcer = TenantEnforcer(db_session, organization_id=10)
    assert enforcer.safe_get(Recipe, recipe.id).id == recipe.id


def test_safe_get_denies_cross_tenant_access(db_session):
    recipe = _make_recipe(db_session, org_id=10, name="Secret")
    enforcer = TenantEnforcer(db_session, organization_id=99)
    with pytest.raises(HTTPException) as exc:
        enforcer.safe_get(Recipe, recipe.id)
    assert exc.value.status_code == 404


def test_safe_filter_is_tenant_scoped(db_session):
    _make_recipe(db_session, org_id=10, name="A")
    _make_recipe(db_session, org_id=10, name="B")
    _make_recipe(db_session, org_id=99, name="C")
    enforcer = TenantEnforcer(db_session, organization_id=10)
    names = sorted(r.name for r in enforcer.safe_filter(Recipe).all())
    assert names == ["A", "B"]


def test_get_all_returns_only_current_org(db_session):
    _make_recipe(db_session, org_id=10, name="A")
    _make_recipe(db_session, org_id=20, name="B")
    enforcer = TenantEnforcer(db_session, organization_id=10)
    assert len(enforcer.get_all(Recipe)) == 1


def test_safe_create_assigns_organization_automatically(db_session):
    enforcer = TenantEnforcer(db_session, organization_id=7)
    created = enforcer.safe_create(Recipe, name="New", created_at=datetime.utcnow())
    assert created.organization_id == 7
    # And it is visible to the same tenant.
    assert enforcer.safe_get(Recipe, created.id).id == created.id
