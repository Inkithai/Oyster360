"""Tests for the data RetentionService."""
from datetime import datetime, timedelta

from app.models.admin import AuditLog
from app.services.retention_service import RetentionService


def _log(db, days_old, action="login"):
    db.add(AuditLog(user_id=1, action=action, created_at=datetime.utcnow() - timedelta(days=days_old)))
    db.commit()


def test_cleanup_removes_only_old_logs(db_session):
    _log(db_session, days_old=400, action="old")
    _log(db_session, days_old=10, action="recent")
    result = RetentionService(db_session).cleanup_old_audit_logs(days=365)
    assert result["deleted_logs"] == 1
    remaining = db_session.query(AuditLog).all()
    assert len(remaining) == 1
    assert remaining[0].action == "recent"


def test_cleanup_custom_window(db_session):
    _log(db_session, days_old=50, action="mid")
    result = RetentionService(db_session).cleanup_old_audit_logs(days=30)
    assert result["deleted_logs"] == 1


def test_anonymize_returns_completed(db_session):
    assert RetentionService(db_session).anonymize_old_user_data() == {"status": "completed"}
