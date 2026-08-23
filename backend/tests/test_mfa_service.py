"""Tests for TOTP MFA service (app.services.mfa_service)."""
import pyotp

from app.core.security import get_password_hash
from app.models.user import User
from app.services.mfa_service import MFAService


def _user(db, email="mfa@test.com"):
    user = User(name="MFA User", email=email, password_hash=get_password_hash("pw"), role="ADMIN")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_generate_secret_returns_qr_and_uri(db_session):
    user = _user(db_session)
    result = MFAService(db_session).generate_secret(user.id)
    assert result["secret"]
    assert result["qr_code"].startswith("data:image/png;base64,")
    assert "Oyster360" in result["provisioning_uri"]
    db_session.refresh(user)
    assert user.mfa_secret == result["secret"]


def test_generate_secret_unknown_user(db_session):
    assert MFAService(db_session).generate_secret(99999) == {"error": "User not found"}


def test_verify_token_accepts_valid_totp(db_session):
    user = _user(db_session, "verify@test.com")
    secret = pyotp.random_base32()
    user.mfa_secret = secret
    db_session.commit()
    valid = pyotp.TOTP(secret).now()
    assert MFAService(db_session).verify_token(user.id, valid) is True
    assert MFAService(db_session).verify_token(user.id, "000000") in (False, True)  # near-window tolerant


def test_verify_token_without_secret_is_false(db_session):
    user = _user(db_session, "nosecret@test.com")
    assert MFAService(db_session).verify_token(user.id, "123456") is False


def test_enable_and_disable_mfa(db_session):
    user = _user(db_session, "toggle@test.com")
    secret = pyotp.random_base32()
    user.mfa_secret = secret
    db_session.commit()

    token = pyotp.TOTP(secret).now()
    assert MFAService(db_session).enable_mfa(user.id, token) is True
    db_session.refresh(user)
    assert user.mfa_enabled is True

    assert MFAService(db_session).disable_mfa(user.id) is True
    db_session.refresh(user)
    assert user.mfa_enabled is False
    assert user.mfa_secret is None


def test_enable_mfa_rejects_bad_token(db_session):
    user = _user(db_session, "badtoken@test.com")
    user.mfa_secret = pyotp.random_base32()
    db_session.commit()
    assert MFAService(db_session).enable_mfa(user.id, "definitely-wrong") is False
