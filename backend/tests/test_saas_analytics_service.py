"""Tests for SaaSAnalyticsService growth, revenue and usage metrics."""
from datetime import datetime, timedelta

from app.models.batch import Batch
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.user import User
from app.services.saas_analytics_service import SaaSAnalyticsService


def _org(db, slug, owner_id=None):
    org = Organization(name=slug.title(), slug=slug, owner_id=owner_id, created_at=datetime.utcnow())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def test_growth_metrics_empty(db_session):
    m = SaaSAnalyticsService(db_session).get_growth_metrics(days=30)
    assert m["total_users"] == 0
    assert m["total_organizations"] == 0
    assert m["user_growth_rate"] == 0


def test_growth_metrics_counts(db_session):
    db_session.add_all([
        User(name="U1", email="u1@x.com", password_hash="h", created_at=datetime.utcnow()),
        User(name="U2", email="u2@x.com", password_hash="h", created_at=datetime.utcnow() - timedelta(days=100)),
    ])
    _org(db_session, "recent")
    db_session.commit()
    m = SaaSAnalyticsService(db_session).get_growth_metrics(days=30)
    assert m["total_users"] == 2
    assert m["new_users"] == 1  # only the one within 30 days
    assert m["total_organizations"] == 1


def test_revenue_metrics(db_session):
    org = _org(db_session, "bill")
    db_session.add_all([
        Subscription(organization_id=org.id, plan="starter", status="active", created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        Subscription(organization_id=org.id, plan="pro", status="active", created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        Subscription(organization_id=org.id, plan="enterprise", status="canceled", created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
    ])
    db_session.commit()
    m = SaaSAnalyticsService(db_session).get_revenue_metrics()
    assert m["active_subscriptions"] == 2
    assert m["monthly_recurring_revenue"] == 29 + 99
    assert m["average_revenue_per_user"] == round((29 + 99) / 2, 2)


def test_usage_metrics(db_session):
    db_session.add_all([
        Batch(batch_number="A", organization_id=1, status="active"),
        Batch(batch_number="B", organization_id=1, status="active"),
        Batch(batch_number="C", organization_id=1, status="completed"),
    ])
    db_session.commit()
    m = SaaSAnalyticsService(db_session).get_usage_metrics()
    assert m["total_batches_created"] == 3
    assert m["currently_active_batches"] == 2
    assert m["batch_utilization"] == round(2 / 3 * 100, 2)


def test_ai_usage_metrics_shape(db_session):
    m = SaaSAnalyticsService(db_session).get_ai_usage_metrics()
    assert {"ai_assistant_queries", "image_analyses", "yield_predictions"} <= set(m)
