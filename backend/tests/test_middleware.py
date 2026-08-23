"""Tests for the shared HTTP middleware (app.core.middleware)."""
import re

from app.core.middleware import SECURITY_HEADERS, add_request_id, add_security_headers
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


def test_security_headers_present_on_every_response():
    response = client.get("/health")

    assert response.status_code == 200
    for header, value in SECURITY_HEADERS.items():
        assert response.headers[header] == value


def test_request_id_header_is_uuid_and_repeats_differ():
    first = client.get("/health")
    second = client.get("/health")

    assert UUID_RE.match(first.headers["X-Request-ID"])
    assert UUID_RE.match(second.headers["X-Request-ID"])
    assert first.headers["X-Request-ID"] != second.headers["X-Request-ID"]


def test_middleware_names_exported_for_documentation():
    # app.main registers these directly; assert the module keeps them callable
    # so accidental removal fails here rather than at boot time.
    assert callable(add_security_headers)
    assert callable(add_request_id)
