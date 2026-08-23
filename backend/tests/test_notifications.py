"""
Notifications API Tests

Covers the /api/notifications router and NotificationService: listing with
unread filtering, ownership checks on mark-as-read, persistence of payload
fields, and authentication enforcement.
"""
from datetime import datetime

import pytest

from app.core.security import create_access_token, get_password_hash
from app.models.user import User, UserRole
from app.services.notification_service import NotificationService


@pytest.fixture
def two_users(db_session):
    alpha = User(
        name="Alpha User",
        email="alpha@oyster360.test",
        password_hash=get_password_hash("alphapass123"),
        role=UserRole.FARM_MANAGER,
    )
    beta = User(
        name="Beta User",
        email="beta@oyster360.test",
        password_hash=get_password_hash("betapass123"),
        role=UserRole.WORKER,
    )
    db_session.add_all([alpha, beta])
    db_session.commit()
    return alpha, beta


def _headers(user):
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def alpha_notifications(db_session, two_users):
    alpha, beta = two_users
    service = NotificationService(db_session)

    older = service.create_notification(
        user_id=alpha.id,
        title="Batch update",
        message="BATCH-42 entered fruiting",
        category="harvest",
        data={"batch_id": 42},
    )
    # Make the older notification already-read to exercise the unread filter.
    older.is_read = True
    newer = service.create_notification(
        user_id=alpha.id,
        title="Welcome",
        message="Your farm workspace is ready",
        category="system",
    )
    # A notification owned by beta that must never appear for alpha.
    service.create_notification(
        user_id=beta.id,
        title="Beta only",
        message="This belongs to another user",
        category="system",
    )
    db_session.commit()
    return {"older": older, "newer": newer}


class TestNotificationService:
    def test_create_notification_persists_payload_fields(
        self, db_session, two_users
    ):
        alpha, _ = two_users
        notification = NotificationService(db_session).create_notification(
            user_id=alpha.id,
            title="Low stock",
            message="Spawn running low",
            category="system",
            data={"item_id": 7},
        )

        assert notification.id is not None
        assert notification.user_id == alpha.id
        assert notification.title == "Low stock"
        assert notification.category == "system"
        assert notification.data == {"item_id": 7}
        assert notification.is_read is False

    def test_create_batch_notification_uses_harvest_category(
        self, db_session, two_users
    ):
        alpha, _ = two_users
        notification = NotificationService(db_session).create_batch_notification(
            alpha.id, "BATCH-77", "Harvest scheduled for tomorrow"
        )

        assert notification.title == "Batch Update: BATCH-77"
        assert notification.category == "harvest"


class TestNotificationsAPI:
    def test_requires_authentication(self, client):
        assert client.get("/api/notifications").status_code == 401

    def test_lists_only_the_callers_notifications_newest_first(
        self, client, two_users, alpha_notifications
    ):
        alpha, _ = two_users

        response = client.get("/api/notifications", headers=_headers(alpha))

        assert response.status_code == 200
        rows = response.json()
        titles = [row["title"] for row in rows]
        assert titles == ["Welcome", "Batch update"]  # newest first
        assert all(row["user_id"] == alpha.id for row in rows)

    def test_unread_only_hides_read_notifications(
        self, client, two_users, alpha_notifications
    ):
        alpha, _ = two_users

        response = client.get(
            "/api/notifications?unread_only=true", headers=_headers(alpha)
        )

        rows = response.json()
        assert [row["title"] for row in rows] == ["Welcome"]

    def test_mark_as_read_is_scoped_to_the_owner(
        self, client, db_session, two_users, alpha_notifications
    ):
        alpha, beta = two_users
        newer = alpha_notifications["newer"]

        # Beta cannot mark alpha's notification as read.
        hijack = client.post(
            f"/api/notifications/{newer.id}/read", headers=_headers(beta)
        )
        assert hijack.status_code == 200
        assert hijack.json() == {"success": False}
        db_session.refresh(newer)
        assert newer.is_read is False

        # The owner can.
        own = client.post(
            f"/api/notifications/{newer.id}/read", headers=_headers(alpha)
        )
        assert own.json() == {"success": True}
        db_session.refresh(newer)
        assert newer.is_read is True
