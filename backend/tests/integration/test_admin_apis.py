import os
import sys
from typing import Any, Dict

from fastapi.testclient import TestClient
import pytest

# Ensure backend/src is on sys.path so imports like "core.*" work
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Use a file-based SQLite DB so the FastAPI app and these tests share the same database
os.environ["DATABASE_URL"] = "sqlite:///./test_app.db"

import main  # noqa: E402
from core.database import Base, engine, get_db  # noqa: E402
from models.user import User  # noqa: E402
from models.role import Role  # noqa: E402
import core.security  # noqa: E402

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


def _ensure_role(name: str) -> Role:
    db = next(get_db())
    role = db.query(Role).filter_by(name=name).first()
    if not role:
        role = Role(name=name)
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


def _ensure_user(email: str, name: str = "User", role_name: str | None = None) -> User:
    db = next(get_db())
    user = db.query(User).filter_by(email=email).first()
    if not user:
        role_id = None
        if role_name:
            role = _ensure_role(role_name)
            role_id = role.id
        user = User(email=email, name=name, password_hash="x", role_id=role_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture(autouse=True)
def patch_get_current_user_superadmin():
    """
    Override dependency for REST endpoints to return a SUPER_ADMIN user.
    This ensures REST admin-only endpoints pass auth checks.
    """
    sa = _ensure_user("sa_admin@example.com", "SA", role_name="SUPER_ADMIN")

    def overridden_get_current_user():
        # Always retrieve fresh instance within current DB session
        db = next(get_db())
        user = db.query(User).filter_by(id=sa.id).first()
        return user

    main.app.dependency_overrides[core.security.get_current_user] = overridden_get_current_user
    yield


def test_graphql_global_analytics_success():
    # Use GraphQL with Super Admin via context getter test header
    sa = _ensure_user("sa_admin@example.com", "SA", role_name="SUPER_ADMIN")
    csrf = _csrf_token()
    headers: Dict[str, Any] = {
        "content-type": "application/json",
        "X-CSRF-Token": csrf,
        "test-user": str(sa.id),  # context_getter will attach this user as SUPER_ADMIN
    }
    cookies = {"hhh_csrf": csrf}
    query = """
    query {
      globalAnalytics {
        period { start end }
        totalUsers
        totalGroups
        totalEntries
        newUsers
        activeUsers
        activeGroups
        engagementRate
      }
    }
    """
    resp = client.post("/graphql", json={"query": query}, headers=headers, cookies=cookies)
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]["globalAnalytics"]
    assert all(k in data for k in ["totalUsers", "totalGroups", "totalEntries"])


def test_rest_backup_trigger_logs_stats_and_graphql_trigger():
    # REST trigger (POST) requires CSRF
    csrf = _csrf_token()
    headers = {"X-CSRF-Token": csrf}
    cookies = {"hhh_csrf": csrf}
    r = client.post("/api/v1/backups/trigger", headers=headers, cookies=cookies)
    assert r.status_code == 200, r.text
    assert r.json().get("success") is True

    # REST logs (GET)
    r_logs = client.get("/api/v1/backups/logs")
    assert r_logs.status_code == 200, r_logs.text
    assert isinstance(r_logs.json(), list)

    # REST stats (GET)
    r_stats = client.get("/api/v1/backups/stats")
    assert r_stats.status_code == 200, r_stats.text
    stats = r_stats.json()
    assert isinstance(stats, dict)

    # GraphQL triggerBackup (mutation)
    sa = _ensure_user("sa_admin@example.com", "SA", role_name="SUPER_ADMIN")
    headers_gql: Dict[str, Any] = {
        "content-type": "application/json",
        "X-CSRF-Token": csrf,
        "test-user": str(sa.id),
    }
    mutation = """
    mutation {
      triggerBackup { success backupId message }
    }
    """
    r_gql = client.post("/graphql", json={"query": mutation}, headers=headers_gql, cookies=cookies)
    assert r_gql.status_code == 200, r_gql.text
    payload = r_gql.json()["data"]["triggerBackup"]
    assert payload["success"] is True


def test_gdpr_graphql_export_and_delete_account():
    # Create a dedicated user for this test
    u = _ensure_user("gdpr_user@example.com", "GDPRUser")
    # Also ensure a SUPER_ADMIN for reliable GraphQL context auth
    sa = _ensure_user("sa_admin@example.com", "SA", role_name="SUPER_ADMIN")
    csrf = _csrf_token()
    headers: Dict[str, Any] = {
        "content-type": "application/json",
        "X-CSRF-Token": csrf,
        # Use SUPER_ADMIN id to ensure authenticated context in GraphQL mutations
        "test-user": str(sa.id),
    }
    cookies = {"hhh_csrf": csrf}

    # Export my data
    export_mut = "mutation { exportMyData { success data message } }"
    r_export = client.post("/graphql", json={"query": export_mut}, headers=headers, cookies=cookies)
    assert r_export.status_code == 200, r_export.text
    export = r_export.json()["data"]["exportMyData"]
    assert "success" in export

    # Delete my account (confirm: true)
    delete_mut = "mutation { deleteMyAccount(confirm: true) { success message } }"
    r_delete = client.post("/graphql", json={"query": delete_mut}, headers=headers, cookies=cookies)
    assert r_delete.status_code == 200, r_delete.text
    delete_res = r_delete.json()["data"]["deleteMyAccount"]
    assert "success" in delete_res


def test_audit_logs_graphql_accessible_to_superadmin():
    sa = _ensure_user("sa_admin@example.com", "SA", role_name="SUPER_ADMIN")
    csrf = _csrf_token()
    headers: Dict[str, Any] = {
        "content-type": "application/json",
        "X-CSRF-Token": csrf,
        "test-user": str(sa.id),  # context_getter attaches SUPER_ADMIN role for tests
    }
    cookies = {"hhh_csrf": csrf}
    query = """
    query {
      auditLogs(limit: 10, offset: 0) {
        id
        action
        userId
        createdAt
      }
    }
    """
    resp = client.post("/graphql", json={"query": query}, headers=headers, cookies=cookies)
    assert resp.status_code == 200, resp.text
    # Response may be empty list; the primary check here is access and shape
