from datetime import datetime
from unittest.mock import Mock

from app.database.database import get_db
from app.main import app


def test_health_endpoint_is_dependency_free_and_traceable(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "oyster360-backend"
    assert datetime.fromisoformat(response.json()["timestamp"]).tzinfo is not None
    assert response.headers["x-request-id"]


def test_readiness_reports_database_failure(client):
    unavailable_db = Mock()
    unavailable_db.execute.side_effect = RuntimeError("credentials must not leak")

    def override_unavailable_db():
        yield unavailable_db

    app.dependency_overrides[get_db] = override_unavailable_db
    try:
        response = client.get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert response.json()["database"] == "unavailable"
    assert "credentials" not in response.text
