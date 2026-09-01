"""Tests for feature gating / subscription access (app.core.feature_gating)."""
from datetime import datetime

from app.core.feature_gating import check_feature_access
from app.models.subscription import Subscription


def _make_subscription(db, org_id, plan, status="active"):
    sub = Subscription(
        organization_id=org_id,
        plan=plan,
        status=status,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(sub)
    db.commit()
    return sub


def test_no_subscription_denies_everything(db_session):
    assert check_feature_access(organization_id=1, feature="basic_batches", db=db_session) is False


def test_free_plan_has_basic_features(db_session):
    _make_subscription(db_session, org_id=1, plan="free")
    assert check_feature_access(1, "basic_batches", db_session) is True
    assert check_feature_access(1, "ai_assistant", db_session) is False


def test_starter_plan_unlocks_ai(db_session):
    _make_subscription(db_session, org_id=1, plan="starter")
    assert check_feature_access(1, "ai_assistant", db_session) is True
    assert check_feature_access(1, "unlimited_batches", db_session) is False


def test_pro_plan_unlocks_advanced(db_session):
    _make_subscription(db_session, org_id=1, plan="pro")
    assert check_feature_access(1, "advanced_analytics", db_session) is True
    assert check_feature_access(1, "team_management", db_session) is True


def test_enterprise_has_all(db_session):
    _make_subscription(db_session, org_id=1, plan="enterprise")
    assert check_feature_access(1, "anything_made_up", db_session) is True


def test_inactive_subscription_denies(db_session):
    _make_subscription(db_session, org_id=1, plan="pro", status="canceled")
    assert check_feature_access(1, "basic_batches", db_session) is False


# ---------------------------------------------------------------------------
# require_subscription decorator: plan-level enforcement on route handlers.
# ---------------------------------------------------------------------------
import asyncio

import pytest
from fastapi import HTTPException
from types import SimpleNamespace

from app.core.feature_gating import require_subscription


@require_subscription("pro")
async def _pro_endpoint(*, current_user=None, db=None):
    return {"ok": True}


def _user(org_id=1):
    return SimpleNamespace(id=1, current_organization_id=org_id)


def _run(coro):
    """Execute an async route handler without pulling in an asyncio plugin."""
    return asyncio.run(coro)


def test_require_subscription_allows_matching_plan(db_session):
    _make_subscription(db_session, org_id=1, plan="pro")

    assert _run(_pro_endpoint(current_user=_user(), db=db_session)) == {"ok": True}


def test_require_subscription_allows_higher_plan(db_session):
    _make_subscription(db_session, org_id=1, plan="enterprise")

    assert _run(_pro_endpoint(current_user=_user(), db=db_session)) == {"ok": True}


def test_require_subscription_rejects_lower_plan(db_session):
    _make_subscription(db_session, org_id=1, plan="starter")

    with pytest.raises(HTTPException) as exc:
        _run(_pro_endpoint(current_user=_user(), db=db_session))

    assert exc.value.status_code == 403
    assert "pro plan or higher" in exc.value.detail


def test_require_subscription_rejects_unknown_plan_name(db_session):
    _make_subscription(db_session, org_id=1, plan="legacy-beta")

    with pytest.raises(HTTPException) as exc:
        _run(_pro_endpoint(current_user=_user(), db=db_session))

    assert exc.value.status_code == 403


def test_require_subscription_rejects_missing_subscription(db_session):
    with pytest.raises(HTTPException) as exc:
        _run(_pro_endpoint(current_user=_user(), db=db_session))

    assert exc.value.status_code == 403
    assert exc.value.detail == "Active subscription required"


def test_require_subscription_rejects_canceled_subscription(db_session):
    _make_subscription(db_session, org_id=1, plan="enterprise", status="canceled")

    with pytest.raises(HTTPException) as exc:
        _run(_pro_endpoint(current_user=_user(), db=db_session))

    assert exc.value.status_code == 403


def test_require_subscription_requires_authentication(db_session):
    with pytest.raises(HTTPException) as exc:
        _run(_pro_endpoint(current_user=None, db=db_session))

    assert exc.value.status_code == 401


def test_require_subscription_requires_a_database_session():
    with pytest.raises(HTTPException) as exc:
        _run(_pro_endpoint(current_user=_user(), db=None))

    assert exc.value.status_code == 500


def test_require_subscription_isolates_organizations(db_session):
    """A pro subscription belonging to another tenant must not grant access."""
    _make_subscription(db_session, org_id=2, plan="pro")

    with pytest.raises(HTTPException) as exc:
        _run(_pro_endpoint(current_user=_user(org_id=1), db=db_session))

    assert exc.value.status_code == 403
