# Security utilities: password hashing, JWT creation/verification, and TOTP helpers.
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt  # PyJWT
import pyotp
from passlib.context import CryptContext

from .config import settings

# Password hashing (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
    to_encode.update({"exp": expire})
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
    to_encode.update({"exp": expire, "type": "refresh"})
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
