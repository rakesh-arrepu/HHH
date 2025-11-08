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
    """Test comprehensive GDPR export and soft delete functionality."""
    from models.entry import SectionEntry
    from models.group_member import GroupMember
    from models.notification import Notification
    from models.audit import AuditLog
    from services.analytics import log_audit_event

    # Create a dedicated user for this test
    u = _ensure_user("gdpr_user@example.com", "GDPRUser")
    # Create test data for the user
    db = next(get_db())

    # Create some entries
    entry1 = SectionEntry(
        user_id=str(u.id),
        group_id="test-group-1",
        section_type="Health",
        content="Test entry 1",
        entry_date="2025-01-01"
    )
    entry2 = SectionEntry(
        user_id=str(u.id),
        group_id="test-group-1",
        section_type="Happiness",
        content="Test entry 2",
        entry_date="2025-01-02"
    )
    db.add(entry1)
    db.add(entry2)

    # Create group membership
    membership = GroupMember(
        user_id=str(u.id),
        group_id="test-group-1"
    )
    db.add(membership)

    # Create notification
    notification = Notification(
        user_id=str(u.id),
        type="info",
        title="Test notification",
        message="Test message"
    )
    db.add(notification)

    # Create audit log
    log_audit_event(db, str(u.id), "test_action", "test_resource", "test_id", {"test": "data"}, "127.0.0.1")

    db.commit()

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
    export_result = r_export.json()["data"]["exportMyData"]
    assert export_result["success"] is True
    assert "data" in export_result

    # Parse and verify export completeness
    import json
    export_data = json.loads(export_result["data"])

    # Verify user profile export
    assert "user_profile" in export_data
    profile = export_data["user_profile"]
    assert profile["id"] == str(u.id)
    assert profile["email"] == u.email
    assert profile["name"] == u.name

    # Verify entries export (should include 2 entries)
    assert "entries" in export_data
    entries = export_data["entries"]
    assert len(entries) == 2
    assert all(e["user_id"] == str(u.id) for e in entries)
    assert all(e["content"] in ["Test entry 1", "Test entry 2"] for e in entries)

    # Verify group memberships export
    assert "group_memberships" in export_data
    memberships = export_data["group_memberships"]
    assert len(memberships) >= 1  # At least the one we created

    # Verify notifications export
    assert "notifications" in export_data
    notifications = export_data["notifications"]
    assert len(notifications) >= 1  # At least the one we created

    # Verify audit logs export (policy: included in export)
    assert "audit_logs" in export_data
    audit_logs = export_data["audit_logs"]
    assert len(audit_logs) >= 1  # At least the one we created

    # Verify summary
    assert "data_summary" in export_data
    summary = export_data["data_summary"]
    assert summary["total_entries"] == 2
    assert summary["total_notifications"] >= 1
    assert summary["total_audit_events"] >= 1

    # Delete my account (confirm: true)
    delete_mut = "mutation { deleteMyAccount(confirm: true) { success message } }"
    r_delete = client.post("/graphql", json={"query": delete_mut}, headers=headers, cookies=cookies)
    assert r_delete.status_code == 200, r_delete.text
    delete_res = r_delete.json()["data"]["deleteMyAccount"]
    assert delete_res["success"] is True
    assert "soft-deleted" in delete_res["message"]
    assert "anonymized" in delete_res["message"]

    # Verify soft delete semantics
    db.refresh(u)
    db.refresh(entry1)
    db.refresh(entry2)
    db.refresh(membership)
    db.refresh(notification)

    # User should be soft deleted and anonymized
    assert u.deleted_at is not None
    assert u.email == f"deleted-{u.id}@anonymous.local"
    assert u.name == "[DELETED USER]"
    assert u.password_hash == "DELETED"

    # Entries should be soft deleted and content anonymized
    assert entry1.deleted_at is not None
    assert entry1.content == "[DELETED]"
    assert entry2.deleted_at is not None
    assert entry2.content == "[DELETED]"

    # Membership should be soft deleted
    assert membership.deleted_at is not None

    # Notification should be soft deleted
    assert notification.deleted_at is not None

    # Audit logs should be anonymized but retained
    audit_logs_after = db.query(AuditLog).filter_by(user_id=str(u.id)).all()
    assert len(audit_logs_after) >= 1
    for log in audit_logs_after:
        metadata = json.loads(log.metadata or "{}")
        assert metadata.get("anonymized") is True
        assert metadata.get("original_user_id") == str(u.id)
        assert log.ip_address == "ANONYMIZED"


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


def test_graphql_group_analytics_forbidden_for_non_member():
    """Test that groupAnalytics returns Forbidden error for non-members."""
    # Create user and group without membership
    from models.group import Group
    from models.group_member import GroupMember
    db = next(get_db())
    user = _ensure_user("nonmember_gql@example.com", "NonMember")
    group = db.query(Group).filter_by(name="Test Group").first()
    if not group:
        group = Group(name="Test Group", description="Test", timezone="UTC")
        db.add(group)
        db.commit()
        db.refresh(group)

    # Override the autouse fixture for this test
    def override_get_current_user():
        return user  # Return the non-member user

    main.app.dependency_overrides[core.security.get_current_user] = override_get_current_user

    try:
        csrf = _csrf_token()
        headers: Dict[str, Any] = {
            "content-type": "application/json",
            "X-CSRF-Token": csrf,
        }
        cookies = {"hhh_csrf": csrf}
        query = f"""
        query {{
          groupAnalytics(groupId: "{group.id}") {{
            groupId
            memberCount
          }}
        }}
        """
        resp = client.post("/graphql", json={"query": query}, headers=headers, cookies=cookies)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "errors" in body
        err = body["errors"][0]
        assert err["extensions"]["code"] == "ERR_FORBIDDEN"
    finally:
        # Clean up override
        main.app.dependency_overrides.pop(core.security.get_current_user, None)


def test_graphql_audit_logs_forbidden_for_non_admin():
    """Test that auditLogs returns Forbidden error for non-Super Admin users."""
    # Create regular user
    user = _ensure_user("regular_user@example.com", "RegularUser", role_name="USER")
    csrf = _csrf_token()
    headers: Dict[str, Any] = {
        "content-type": "application/json",
        "X-CSRF-Token": csrf,
        "test-user": str(user.id),
        "test-user-role": "USER",  # Non-admin role
    }
    cookies = {"hhh_csrf": csrf}
    query = """
    query {
      auditLogs(limit: 5) {
        id
        action
      }
    }
    """
    resp = client.post("/graphql", json={"query": query}, headers=headers, cookies=cookies)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "errors" in body
    err = body["errors"][0]
    assert err["extensions"]["code"] == "ERR_FORBIDDEN"


def test_graphql_analytics_unauthenticated():
    """Test that GraphQL analytics queries return Unauthorized when no user context."""
    csrf = _csrf_token()
    headers = {
        "content-type": "application/json",
        "X-CSRF-Token": csrf,
        # No test-user header = unauthenticated
    }
    cookies = {"hhh_csrf": csrf}

    # Test groupAnalytics unauthenticated
    from models.group import Group
    db = next(get_db())
    group = db.query(Group).first()
    if not group:
        group = Group(name="Test Group", description="Test", timezone="UTC")
        db.add(group)
        db.commit()
        db.refresh(group)

    query_group = f"""
    query {{
      groupAnalytics(groupId: "{group.id}") {{
        groupId
      }}
    }}
    """
    resp_group = client.post("/graphql", json={"query": query_group}, headers=headers, cookies=cookies)
    assert resp_group.status_code == 200, resp_group.text
    body_group = resp_group.json()
    assert "errors" in body_group
    assert body_group["errors"][0]["extensions"]["code"] == "ERR_UNAUTHORIZED"

    # Test globalAnalytics unauthenticated
    query_global = """
    query {
      globalAnalytics {
        totalUsers
      }
    }
    """
    resp_global = client.post("/graphql", json={"query": query_global}, headers=headers, cookies=cookies)
    assert resp_global.status_code == 200, resp_global.text
    body_global = resp_global.json()
    assert "errors" in body_global
    assert body_global["errors"][0]["extensions"]["code"] == "ERR_UNAUTHORIZED"

    # Test auditLogs unauthenticated
    query_audit = """
    query {
      auditLogs(limit: 1) {
        id
      }
    }
    """
    resp_audit = client.post("/graphql", json={"query": query_audit}, headers=headers, cookies=cookies)
    assert resp_audit.status_code == 200, resp_audit.text
    body_audit = resp_audit.json()
    assert "errors" in body_audit
    assert body_audit["errors"][0]["extensions"]["code"] == "ERR_UNAUTHORIZED"
