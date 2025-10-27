import os
import sys
from typing import Dict, Any

import pytest
import pyotp
from fastapi.testclient import TestClient

# Ensure backend/src is on sys.path so imports like "core.*" work
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Use a file-based SQLite DB so the FastAPI app and this test share the same database
os.environ["DATABASE_URL"] = "sqlite:///./test_app.db"

import main  # noqa: E402
from core.database import Base, engine, get_db  # noqa: E402
from models.user import User  # noqa: E402
from models.role import Role  # noqa: E402
import core.security  # noqa: E402
from core.security import get_password_hash  # noqa: E402

# Create all tables once for this module
Base.metadata.create_all(bind=engine)

client = TestClient(main.app)


def _csrf_token() -> str:
    """Fetch CSRF cookie value by hitting a safe endpoint."""
    r = client.get("/api/v1/auth/health")
    assert r.status_code == 200
    token = client.cookies.get("hhh_csrf")
    assert token is not None
    return token


def _ensure_super_admin_user() -> User:
    """Create (or fetch) a SUPER_ADMIN user in the shared app DB."""
    db = next(get_db())
    role = db.query(Role).filter_by(name="SUPER_ADMIN").first()
    if not role:
        role = Role(name="SUPER_ADMIN")
        db.add(role)
        db.commit()
        db.refresh(role)

    email = "superadmin2fa@example.com"
    user = db.query(User).filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            name="SA2FA",
            password_hash=get_password_hash("password123"),
            role_id=role.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def _reset_2fa(user_id: str):
    """Reset 2FA state for a user to ensure tests are idempotent."""
    db = next(get_db())
    u = db.query(User).filter_by(id=user_id).first()
    if u:
        u.totp_secret = None
        u.is_2fa_enabled = False
        db.commit()


@pytest.fixture(autouse=True)
def patch_get_current_user():
    """
    Override dependency for REST endpoints to always return the SUPER_ADMIN user
    from the shared DB, with role.name populated.
    """
    def overridden_get_current_user():
        db = next(get_db())
        user = db.query(User).filter_by(email="superadmin2fa@example.com").first()
        if not user:
            user = _ensure_super_admin_user()
        return user

    main.app.dependency_overrides[core.security.get_current_user] = overridden_get_current_user
    yield
    # Cleanup not strictly necessary since TestClient/app is module-scoped here


def test_2fa_rest_enable_and_verify():
    # Ensure SUPER_ADMIN exists
    sa = _ensure_super_admin_user()
    _reset_2fa(sa.id)

    # Obtain CSRF cookie and set header for mutating requests
    csrf = _csrf_token()
    headers = {"X-CSRF-Token": csrf}
    cookies = {"hhh_csrf": csrf}

    # Enable 2FA
    resp_enable = client.post("/api/v1/auth/2fa/enable", headers=headers, cookies=cookies)
    assert resp_enable.status_code == 200, resp_enable.text
    uri = resp_enable.json().get("provisioning_uri")
    assert uri and "otpauth://" in uri

    # Generate TOTP code from provisioning URI (avoid cross-session cache issues)
    from urllib.parse import urlparse, parse_qs
    qs = parse_qs(urlparse(uri).query)
    secret = qs.get("secret", [None])[0]
    assert secret, "TOTP secret missing in provisioning URI"
    code = pyotp.TOTP(secret).now()

    # Verify 2FA
    resp_verify = client.post(
        "/api/v1/auth/2fa/verify",
        json={"totp_code": code},
        headers=headers,
        cookies=cookies,
    )
    assert resp_verify.status_code == 200, resp_verify.text
    assert resp_verify.json().get("2fa_enabled") is True


def test_2fa_graphql_enable_and_verify():
    # Ensure SUPER_ADMIN exists
    sa = _ensure_super_admin_user()
    _reset_2fa(sa.id)

    # CSRF cookie/header for mutation POST
    csrf = _csrf_token()
    headers: Dict[str, Any] = {
        "content-type": "application/json",
        "X-CSRF-Token": csrf,
        # hint context_getter to attach this user in GraphQL resolvers
        "test-user": str(sa.id),
    }
    cookies = {"hhh_csrf": csrf}

    # Enable via GraphQL
    enable_query = """
    mutation {
      enable2fa
    }
    """
    resp = client.post("/graphql", json={"query": enable_query}, headers=headers, cookies=cookies)
    assert resp.status_code == 200, resp.text
    provisioning_uri = resp.json()["data"]["enable2fa"]
    assert provisioning_uri and "otpauth://" in provisioning_uri

    # Read secret from DB and verify
    db = next(get_db())
    user = db.query(User).filter_by(id=sa.id).first()
    assert user and user.totp_secret, "TOTP secret should be stored after enable"
    code = pyotp.TOTP(user.totp_secret).now()

    verify_query = """
    mutation Verify2FA($code: String!) {
      verify2fa(totpCode: $code)
    }
    """
    resp_verify = client.post(
        "/graphql",
        json={"query": verify_query, "variables": {"code": code}},
        headers=headers,
        cookies=cookies,
    )
    assert resp_verify.status_code == 200, resp_verify.text
    assert resp_verify.json()["data"]["verify2fa"] is True
