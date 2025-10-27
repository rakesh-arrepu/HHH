import os
import sys
import uuid
from typing import Any, Dict, Optional

import pytest
from fastapi.testclient import TestClient

# Ensure backend/src is on sys.path so imports like "core.*" and "models.*" work in tests
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Use a file-based SQLite DB so the FastAPI app and these tests share the same database
os.environ["DATABASE_URL"] = "sqlite:///./test_app.db"

import main  # noqa: E402
import core.security  # noqa: E402
from core.database import Base, engine, get_db  # noqa: E402
from models.user import User  # noqa: E402
from models.role import Role  # noqa: E402
from models.group import Group  # noqa: E402
from models.group_member import GroupMember  # noqa: E402

# Create all tables once for this module (file DB reused across tests in this file)
Base.metadata.create_all(bind=engine)
client = TestClient(main.app)


def _db():
    return next(get_db())


def _ensure_role(name: str) -> Role:
    db = _db()
    role = db.query(Role).filter_by(name=name).first()
    if not role:
        role = Role(name=name)
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


def _create_user(email: str, name: str = "User", role_name: Optional[str] = None) -> User:
    """
    Create a user with optional role assignment.
    Ensure unique email to avoid collisions between tests in shared SQLite DB.
    """
    db = _db()
    if "@" in email:
        local, domain = email.split("@", 1)
        email_unique = f"{local}+{uuid.uuid4().hex[:8]}@{domain}"
    else:
        email_unique = f"{email}-{uuid.uuid4().hex[:8]}"
    role_id = None
    if role_name:
        role = _ensure_role(role_name)
        role_id = role.id
    user = User(email=email_unique, name=name, password_hash="x", role_id=role_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_group(name: str = "G", description: str = "Desc", admin_id: Optional[str] = None) -> Group:
    db = _db()
    g = Group(name=name, description=description, admin_id=admin_id)
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


def _add_member(group_id: str, user_id: str) -> GroupMember:
    db = _db()
    m = GroupMember(group_id=group_id, user_id=user_id)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def _override_current_user(user_id: str, role_name: Optional[str] = None):
    """
    Override dependency to return a real DB user with optional role attached.
    Ensures REST endpoints using Depends(get_current_user) see an authenticated user.
    """
    def overridden_get_current_user():
        db = _db()
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            # Fallback minimal object to avoid test crash if user disappeared
            class Dummy:
                id = user_id
                role = type("R", (), {"name": role_name})() if role_name else None
            return Dummy()
        if role_name:
            # Attach role if not present; helpful for SUPER_ADMIN checks
            if not getattr(getattr(user, "role", None), "name", None):
                user.role = type("R", (), {"name": role_name})()  # type: ignore
        return user

    main.app.dependency_overrides[core.security.get_current_user] = overridden_get_current_user


def _clear_overrides():
    main.app.dependency_overrides.pop(core.security.get_current_user, None)


def _csrf_token() -> str:
    """Fetch CSRF cookie value by hitting a safe endpoint."""
    r = client.get("/api/v1/auth/health")
    assert r.status_code == 200
    token = client.cookies.get("hhh_csrf")
    assert token is not None
    return token


# ------------- REST envelope tests ------------- #

def test_rest_unauthorized_envelope_on_protected_route():
    """
    Expect 401 with standardized envelope when no user is present.
    """
    _clear_overrides()
    resp = client.get("/api/v1/analytics/group/some-group-id")
    assert resp.status_code == 401, resp.text
    j = resp.json()
    # Envelope top-level
    assert j.get("code") == "ERR_UNAUTHORIZED"
    assert j.get("message") in ["Not authenticated", "Unauthorized"]
    # Compatible legacy FastAPI field
    assert "detail" in j
    # Observability fields
    assert "timestamp" in j
    assert j.get("path") == "/api/v1/analytics/group/some-group-id"
    # Correlation may be None or string, but key must exist
    assert "correlationId" in j


def test_rest_forbidden_envelope_when_not_member_or_admin():
    """
    Expect 403 when authenticated but not a member/admin of the group.
    """
    u = _create_user("rest_forbid@example.com")
    g = _create_group()
    _override_current_user(user_id=str(u.id), role_name=None)

    resp = client.get(f"/api/v1/analytics/group/{g.id}")
    assert resp.status_code == 403, resp.text
    j = resp.json()
    assert j.get("code") == "ERR_FORBIDDEN"
    assert j.get("detail") in ["Not authorized to view this group's analytics"]
    assert j.get("path") == f"/api/v1/analytics/group/{g.id}"
    assert "timestamp" in j
    assert "correlationId" in j


def test_rest_not_found_envelope_for_missing_group():
    """
    Expect 404 when group does not exist.
    """
    u = _create_user("rest_notfound@example.com")
    _override_current_user(user_id=str(u.id), role_name=None)

    missing = "00000000-0000-0000-0000-000000000000"
    resp = client.get(f"/api/v1/analytics/group/{missing}")
    assert resp.status_code == 404, resp.text
    j = resp.json()
    assert j.get("code") == "ERR_NOT_FOUND"
    assert j.get("detail") in ["Group not found", "Not Found"]
    assert j.get("path") == f"/api/v1/analytics/group/{missing}"
    assert "timestamp" in j
    assert "correlationId" in j


def test_rest_validation_envelope_request_validation_error():
    """
    Expect 422 with standardized envelope when query parameter fails validation.
    """
    sa = _create_user("sa_rest_val@example.com", role_name="SUPER_ADMIN")
    _override_current_user(user_id=str(sa.id), role_name="SUPER_ADMIN")

    # Invalid date for start_date triggers FastAPI RequestValidationError
    resp = client.get("/api/v1/analytics/global?start_date=not-a-date")
    assert resp.status_code == 422, resp.text
    j = resp.json()
    assert j.get("code") == "ERR_VALIDATION"
    assert j.get("message") == "Validation error"
    assert "details" in j and isinstance(j["details"].get("errors", []), list)
    assert "timestamp" in j
    assert j.get("path") == "/api/v1/analytics/global"


# ------------- GraphQL envelope tests ------------- #

def test_graphql_unauthorized_extensions_code_on_query():
    """
    dailyProgress requires auth -> should raise Unauthorized mapped to extensions.code=ERR_UNAUTHORIZED
    """
    query = """
    query($d: Date!) {
      dailyProgress(date: $d) { date totalEntries }
    }
    """
    # No test-user header provided -> unauthorized
    resp = client.post("/graphql", json={"query": query, "variables": {"d": "2025-01-01"}})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "errors" in body and isinstance(body["errors"], list)
    err = body["errors"][0]
    assert err.get("extensions", {}).get("code") == "ERR_UNAUTHORIZED"
    assert "correlationId" in err.get("extensions", {})
    assert "path" in err.get("extensions", {})


def test_graphql_forbidden_extensions_code_on_query():
    """
    globalAnalytics requires SUPER_ADMIN; simulate a normal USER role via headers.
    """
    user = _create_user("gql_forbid@example.com")  # no SUPER_ADMIN role
    headers = {
        "content-type": "application/json",
        "test-user": str(user.id),
        "test-user-role": "USER",
    }
    query = "query { globalAnalytics { totalUsers } }"
    resp = client.post("/graphql", json={"query": query}, headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "errors" in body
    err = body["errors"][0]
    assert err.get("extensions", {}).get("code") == "ERR_FORBIDDEN"
    assert "correlationId" in err.get("extensions", {})


def test_graphql_validation_extensions_code_on_mutation():
    """
    create_entry with empty content -> ValidationError mapped to ERR_VALIDATION.
    """
    # Prepare user + group
    user = _create_user("gql_val@example.com")
    group = _create_group()
    csrf = _csrf_token()
    headers = {
        "content-type": "application/json",
        "X-CSRF-Token": csrf,  # required for mutations
        "test-user": str(user.id),
    }
    cookies = {"hhh_csrf": csrf}

    mutation = """
    mutation($input: CreateEntryInput!) {
      createEntry(input: $input) { id content section_type }
    }
    """
    variables = {
        "input": {
            "user_id": str(user.id),
            "group_id": str(group.id),
            "section_type": "Health",
            "content": "   "  # invalid -> will be stripped and rejected
        }
    }
    resp = client.post("/graphql", json={"query": mutation, "variables": variables}, headers=headers, cookies=cookies)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "errors" in body
    err = body["errors"][0]
    assert err.get("extensions", {}).get("code") == "ERR_VALIDATION"
    assert "correlationId" in err.get("extensions", {})


def test_graphql_not_found_extensions_code_on_mutation():
    """
    delete_entry for a non-existing id -> NotFoundError mapped to ERR_NOT_FOUND.
    """
    user = _create_user("gql_nf@example.com")
    csrf = _csrf_token()
    headers = {
        "content-type": "application/json",
        "X-CSRF-Token": csrf,
        "test-user": str(user.id),
    }
    cookies = {"hhh_csrf": csrf}

    mutation = """
    mutation {
      deleteEntry(id: "00000000-0000-0000-0000-000000000000")
    }
    """
    resp = client.post("/graphql", json={"query": mutation}, headers=headers, cookies=cookies)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "errors" in body
    err = body["errors"][0]
    assert err.get("extensions", {}).get("code") == "ERR_NOT_FOUND"
    assert "correlationId" in err.get("extensions", {})


# ------------- Cleanup / Safety ------------- #

@pytest.fixture(autouse=True)
def _cleanup_overrides():
    """
    Ensure dependency overrides do not leak between tests in this module.
    """
    yield
    _clear_overrides()
