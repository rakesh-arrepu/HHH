# Security utilities: password hashing, JWT creation/verification, and TOTP helpers.
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

import jwt  # PyJWT
import pyotp
from passlib.context import CryptContext
from fastapi import Response

from .config import settings

# Password hashing (bcrypt)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


# JWT helpers
def create_access_token(
    data: Dict[str, Any],
    expires_minutes: Optional[int] = None,
    secret: Optional[str] = None,
    algorithm: Optional[str] = None,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes if expires_minutes is not None else settings.access_token_exp_minutes
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    token = jwt.encode(
        to_encode,
        key=secret or settings.jwt_secret,
        algorithm=algorithm or settings.jwt_algorithm,
    )
    return token


def create_refresh_token(
    data: Dict[str, Any],
    expires_days: Optional[int] = None,
    secret: Optional[str] = None,
    algorithm: Optional[str] = None,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=expires_days if expires_days is not None else settings.refresh_token_exp_days
    )
    to_encode.update(
        {"exp": expire, "type": "refresh", "iat": datetime.now(timezone.utc), "jti": str(uuid4())}
    )
    token = jwt.encode(
        to_encode,
        key=secret or settings.jwt_secret,
        algorithm=algorithm or settings.jwt_algorithm,
    )
    return token


def decode_token(token: str, secret: Optional[str] = None, algorithms: Optional[list[str]] = None) -> Dict[str, Any]:
    payload = jwt.decode(
        token,
        key=secret or settings.jwt_secret,
        algorithms=algorithms or [settings.jwt_algorithm],
        options={"require": ["exp"]},
    )
    return payload


# TOTP (2FA) helpers
def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_uri(email: str, secret: str) -> str:
    # otpauth URI can be converted into a QR code by the client
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=settings.totp_issuer)


def verify_totp_code(secret: str, code: str, valid_window: int = 1) -> bool:
    """valid_window allows slight clock skew (e.g., 30s steps)."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=valid_window)


# Cookie helpers for httpOnly JWT cookies
def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """
    Set httpOnly cookies for access and refresh tokens.
    - SameSite=Lax for CSRF-safe default
    - Secure flag from settings.secure_cookies
    - Domain from settings.cookie_domain (or host-only if empty)
    Note: We set both cookies in a single 'set-cookie' header so a single header read includes both cookies.
    """
    def build_cookie(name: str, value: str) -> str:
        parts = [
            f"{name}={value}",
            "HttpOnly",
            "Path=/",
            "SameSite=lax",
        ]
        if settings.secure_cookies:
            parts.append("Secure")
        if settings.cookie_domain:
            parts.append(f"Domain={settings.cookie_domain}")
        return "; ".join(parts)

    access_cookie = build_cookie(settings.access_cookie_name, access_token)
    refresh_cookie = build_cookie(settings.refresh_cookie_name, refresh_token)
    response.headers["set-cookie"] = f"{access_cookie}, {refresh_cookie}"


def clear_auth_cookies(response: Response) -> None:
    """Clear access and refresh cookies."""
    def expired_cookie(name: str) -> str:
        parts = [
            f"{name}=; Max-Age=0",
            "Expires=Thu, 01 Jan 1970 00:00:00 GMT",
            "HttpOnly",
            "Path=/",
            "SameSite=lax",
        ]
        if settings.secure_cookies:
            parts.append("Secure")
        if settings.cookie_domain:
            parts.append(f"Domain={settings.cookie_domain}")
        return "; ".join(parts)

    access_del = expired_cookie(settings.access_cookie_name)
    refresh_del = expired_cookie(settings.refresh_cookie_name)
    response.headers["set-cookie"] = f"{access_del}, {refresh_del}"
