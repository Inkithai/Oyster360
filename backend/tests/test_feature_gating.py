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
