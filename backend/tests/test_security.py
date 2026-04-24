"""Unit tests for password hashing and JWT issuance (app.core.security)."""
from datetime import timedelta

import jwt
import pytest

from app.core import security
from app.core.config import settings


def test_password_hash_roundtrip():
    hashed = security.get_password_hash("s3cret-pass")
    assert hashed != "s3cret-pass"
    assert security.verify_password("s3cret-pass", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = security.get_password_hash("correct-horse-battery")
    assert security.verify_password("nope", hashed) is False
    assert security.verify_password("", hashed) is False


def test_create_access_token_contains_claims_and_expiry():
    token = security.create_access_token({"sub": "42", "role": "ADMIN"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "42"
    assert payload["role"] == "ADMIN"
    assert "exp" in payload


def test_create_access_token_respects_expires_delta():
    token = security.create_access_token(
        {"sub": "7"}, expires_delta=timedelta(seconds=-10)
    )
    # A token already in the past is expired -> decode raises.
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
