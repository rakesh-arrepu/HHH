import pytest
from fastapi.testclient import TestClient
import pyotp

from main import app
from models.user import User
from models.role import Role

client = TestClient(app)

from core.security import get_password_hash

@pytest.fixture
def superadmin_user(db_session):
    # Ensure role exists
    role = db_session.query(Role).filter_by(name="SUPER_ADMIN").first()
    if not role:
        role = Role(name="SUPER_ADMIN")
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
    plain_password = "password123"
    user = User(email="superadmin2fa@example.com", name="SA2FA", password_hash=get_password_hash(plain_password), role_id=role.id)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    user._plain_password = plain_password  # Store for test login
    return user

def login_headers(user):
    # Simulate SuperAdmin context via test-only header
    return {"test-user": str(user.id)}

import core.security

@pytest.fixture(autouse=True)
def patch_get_current_user():
    # Patch get_current_user to fetch a fresh user from the DB with role.name set, per request/session
    def overridden_get_current_user():
        from core.database import get_db
        from models.user import User
        db = next(get_db())
        user = db.query(User).filter_by(email="superadmin2fa@example.com").first()
        class DummyRole:
            name = "SUPER_ADMIN"
        user.role = DummyRole()
        return user
    app.dependency_overrides[core.security.get_current_user] = overridden_get_current_user

# def test_2fa_rest_enable_and_verify(superadmin_user):
#     # Login and get session cookies, then get CSRF cookie
#     login_data = {"email": superadmin_user.email, "password": getattr(superadmin_user, "_plain_password", "password123")}
#     login_resp = client.post("/api/v1/auth/login", json=login_data)
#     assert login_resp.status_code == 200
#     health_resp = client.get("/api/v1/auth/health")
#     csrf_cookie = health_resp.cookies.get("hhh_csrf")
#     at = login_resp.cookies.get("hhh_at")
#     rt = login_resp.cookies.get("hhh_rt")
#     print("DEBUG COOKIES after login: hhh_at:", at, "hhh_rt:", rt, "hhh_csrf:", csrf_cookie)
#     assert at is not None and rt is not None and csrf_cookie is not None
#     cookies = {"hhh_at": at, "hhh_rt": rt, "hhh_csrf": csrf_cookie}
#     headers = login_headers(superadmin_user)
#     headers["X-CSRF-Token"] = csrf_cookie
#     response = client.post("/api/v1/auth/2fa/enable", headers=headers, cookies=cookies)
#     assert response.status_code == 200
#     uri = response.json().get("provisioning_uri")
#     assert "otpauth://" in uri
#     # Get TOTP from DB
#     from core.database import get_db
#     db = next(get_db())
#     user = db.query(User).filter_by(id=superadmin_user.id).first()
#     totp = pyotp.TOTP(user.totp_secret)
#     code = totp.now()
#     headers["X-CSRF-Token"] = csrf_cookie
#     response = client.post("/api/v1/auth/2fa/verify", json={"totp_code": code}, headers=headers, cookies=cookies)
#     assert response.status_code == 200
#     assert response.json()["2fa_enabled"] is True

# def test_2fa_graphql_enable_and_verify(superadmin_user):
#     # Get CSRF cookie from health endpoint
#     resp0 = client.get("/api/v1/auth/health")
#     csrf_cookie = resp0.cookies.get("hhh_csrf")
#     query = '''
#     mutation {
#         enable2fa
#     }
#     '''
#     headers = {**login_headers(superadmin_user), "content-type": "application/json", "X-CSRF-Token": csrf_cookie}
#     cookies = {"hhh_csrf": csrf_cookie}
#     resp = client.post("/graphql", json={"query": query}, headers=headers, cookies=cookies)
#     assert resp.status_code == 200
#     provisioning_uri = resp.json()["data"]["enable2fa"]
#     assert provisioning_uri and "otpauth://" in provisioning_uri
#     from core.database import get_db
#     db = next(get_db())
#     user = db.query(User).filter_by(id=superadmin_user.id).first()
#     totp = pyotp.TOTP(user.totp_secret)
#     code = totp.now()
#     verify_query = '''
#     mutation Verify2fa($code: String!) {
#         verify2fa(totpCode: $code)
#     }
#     '''
#     resp_verify = client.post("/graphql", json={"query": verify_query, "variables": {"code": code}}, headers=headers, cookies=cookies)
#     assert resp_verify.status_code == 200
#     assert resp_verify.json()["data"]["verify2fa"] is True
