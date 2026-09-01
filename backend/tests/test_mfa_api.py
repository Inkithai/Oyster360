"""Tests for the MFA enrolment endpoints.

TOTP codes are generated locally with pyotp against the secret the API just
issued, so the full enrol -> verify -> disable flow is exercised without any
external service or clock skew tolerance games.
"""
from datetime import datetime

import pyotp
import pytest

from app.core.security import create_access_token, get_password_hash
from app.models.user import User


def _headers(user: User) -> dict:
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mfa_user(db_session):
    user = User(
        name="MFA User",
        email="mfa@test.local",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_setup_returns_secret_and_qr_code(client, mfa_user):
    response = client.post("/api/mfa/setup", headers=_headers(mfa_user))

    assert response.status_code == 200
    body = response.json()
    assert body["secret"]
    assert body["qr_code"].startswith("data:image/png;base64,")
    assert "otpauth://totp/" in body["provisioning_uri"]
    assert "Oyster360" in body["provisioning_uri"]


def test_setup_persists_the_secret_but_leaves_mfa_disabled(client, db_session, mfa_user):
    """Enrolment must not take effect until a code is verified."""
    body = client.post("/api/mfa/setup", headers=_headers(mfa_user)).json()

    db_session.refresh(mfa_user)
    assert mfa_user.mfa_secret == body["secret"]
    assert not mfa_user.mfa_enabled


def test_setup_rotates_the_secret_when_called_again(client, mfa_user):
    first = client.post("/api/mfa/setup", headers=_headers(mfa_user)).json()["secret"]
    second = client.post("/api/mfa/setup", headers=_headers(mfa_user)).json()["secret"]

    assert first != second


def test_verify_with_a_valid_code_enables_mfa(client, db_session, mfa_user):
    secret = client.post("/api/mfa/setup", headers=_headers(mfa_user)).json()["secret"]
    code = pyotp.TOTP(secret).now()

    response = client.post(
        "/api/mfa/verify", json={"token": code}, headers=_headers(mfa_user)
    )

    assert response.status_code == 200
    assert response.json() == {"success": True}
    db_session.refresh(mfa_user)
    assert mfa_user.mfa_enabled


def test_verify_with_an_invalid_code_does_not_enable_mfa(client, db_session, mfa_user):
    client.post("/api/mfa/setup", headers=_headers(mfa_user))

    response = client.post(
        "/api/mfa/verify", json={"token": "000000"}, headers=_headers(mfa_user)
    )

    assert response.status_code == 200
    assert response.json() == {"success": False}
    db_session.refresh(mfa_user)
    assert not mfa_user.mfa_enabled


def test_verify_before_setup_fails(client, mfa_user):
    """No secret has been issued, so any code must be rejected."""
    response = client.post(
        "/api/mfa/verify", json={"token": "123456"}, headers=_headers(mfa_user)
    )

    assert response.json() == {"success": False}


def test_verify_rejects_another_users_code(client, db_session, mfa_user):
    other = User(
        name="Other",
        email="other@mfa.test",
        password_hash=get_password_hash("pass123"),
        role="ADMIN",
    )
    db_session.add(other)
    db_session.commit()

    victim_secret = client.post("/api/mfa/setup", headers=_headers(mfa_user)).json()["secret"]
    client.post("/api/mfa/setup", headers=_headers(other))

    # The attacker presents a code derived from the victim's secret.
    response = client.post(
        "/api/mfa/verify",
        json={"token": pyotp.TOTP(victim_secret).now()},
        headers=_headers(other),
    )

    assert response.json() == {"success": False}
    db_session.refresh(other)
    assert not other.mfa_enabled


def test_verify_requires_a_token_field(client, mfa_user):
    response = client.post("/api/mfa/verify", json={}, headers=_headers(mfa_user))

    assert response.status_code == 422


def test_disable_clears_the_secret_and_flag(client, db_session, mfa_user):
    secret = client.post("/api/mfa/setup", headers=_headers(mfa_user)).json()["secret"]
    client.post(
        "/api/mfa/verify", json={"token": pyotp.TOTP(secret).now()}, headers=_headers(mfa_user)
    )

    response = client.post("/api/mfa/disable", headers=_headers(mfa_user))

    assert response.json() == {"success": True}
    db_session.refresh(mfa_user)
    assert not mfa_user.mfa_enabled
    assert mfa_user.mfa_secret is None


def test_disable_is_idempotent(client, mfa_user):
    assert client.post("/api/mfa/disable", headers=_headers(mfa_user)).json() == {"success": True}
    assert client.post("/api/mfa/disable", headers=_headers(mfa_user)).json() == {"success": True}


def test_codes_stop_working_after_disable(client, mfa_user):
    secret = client.post("/api/mfa/setup", headers=_headers(mfa_user)).json()["secret"]
    client.post("/api/mfa/disable", headers=_headers(mfa_user))

    response = client.post(
        "/api/mfa/verify", json={"token": pyotp.TOTP(secret).now()}, headers=_headers(mfa_user)
    )

    assert response.json() == {"success": False}


@pytest.mark.parametrize("path", ["/api/mfa/setup", "/api/mfa/disable"])
def test_mfa_endpoints_require_authentication(client, path):
    assert client.post(path).status_code in (401, 403)


def test_verify_requires_authentication(client):
    assert client.post("/api/mfa/verify", json={"token": "123456"}).status_code in (401, 403)
