import os
import sys
from typing import Dict, Any

import pytest
from fastapi import Response
import pyotp

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_totp_secret,
    get_totp_uri,
    verify_totp_code,
    set_auth_cookies,
    clear_auth_cookies,
)
from core.config import settings


def test_password_hash_and_verify():
    password = "S3cure!Pass"
    hashed = get_password_hash(password)
    assert hashed and isinstance(hashed, str)
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_jwt_create_and_decode_access_token():
    claims: Dict[str, Any] = {"sub": "user-123", "email": "user@example.com"}
    token = create_access_token(claims, expires_minutes=5)  # short expiry for test
    assert isinstance(token, str) and len(token) > 10

    decoded = decode_token(token)
    assert decoded["sub"] == claims["sub"]
    assert decoded["email"] == claims["email"]
    assert "exp" in decoded


def test_refresh_token_has_type_and_rotation_changes_token():
    claims: Dict[str, Any] = {"sub": "user-123", "email": "user@example.com"}
    t1 = create_refresh_token(claims, expires_days=1)
    t2 = create_refresh_token(claims, expires_days=1)
    assert isinstance(t1, str) and isinstance(t2, str)
    assert t1 != t2  # rotation should produce a different token (different iat/exp)
    decoded = decode_token(t1)
    assert decoded.get("type") == "refresh"


def test_totp_generate_uri_and_verify_code():
    secret = generate_totp_secret()
    assert isinstance(secret, str) and len(secret) >= 16

    uri = get_totp_uri("user@example.com", secret)
    assert isinstance(uri, str) and uri.startswith("otpauth://totp/")

    # Generate a current code using pyotp for the same secret and verify
    totp = pyotp.TOTP(secret)
    code = totp.now()
    assert verify_totp_code(secret, code) is True


def test_auth_cookies_set_and_clear():
    response = Response()
    access = create_access_token({"sub": "u1", "email": "e@x.com"}, expires_minutes=5)
    refresh = create_refresh_token({"sub": "u1", "email": "e@x.com"}, expires_days=1)

    set_auth_cookies(response, access, refresh)
    set_cookie_header = response.headers.get("set-cookie")
    assert set_cookie_header is not None
    # Should include both cookie names
    assert settings.access_cookie_name in set_cookie_header
    assert settings.refresh_cookie_name in set_cookie_header

    # Now clear cookies should add delete cookie headers
    response2 = Response()
    clear_auth_cookies(response2)
    del_cookie_header = response2.headers.get("set-cookie")
    # FastAPI/Starlette may add multiple Set-Cookie headers; ensure both names appear
    assert del_cookie_header is not None
    assert settings.access_cookie_name in del_cookie_header
    assert settings.refresh_cookie_name in del_cookie_header
