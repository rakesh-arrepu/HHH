import os
import sys

from fastapi.testclient import TestClient
import uuid

# Ensure backend/src is on sys.path so imports like "core.*" and "models.*" work in tests
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Use a file-based SQLite DB for integration tests to align with other integration tests
os.environ["DATABASE_URL"] = "sqlite:///./test_app.db"

import main  # noqa: E402
import core.security  # noqa: E402
from core.database import Base, engine, get_db  # noqa: E402
from models.user import User  # noqa: E402
from models.role import Role  # noqa: E402
from models.group import Group  # noqa: E402
from models.group_member import GroupMember  # noqa: E402

# Create tables once for this test module (file-based DB is reused)
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


def _create_user(email: str, name: str = "Test User") -> User:
    db = _db()
    # Ensure unique email to avoid cross-test collisions in the shared SQLite file DB
    if "@" in email:
        local, domain = email.split("@", 1)
        unique_email = f"{local}+{uuid.uuid4().hex[:8]}@{domain}"
    else:
        unique_email = f"{email}-{uuid.uuid4().hex[:8]}"
    user = User(email=unique_email, name=name, password_hash="x")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_group(name: str = "Group A", description: str = "Desc", admin_id: str | None = None) -> Group:
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


def _override_current_user(user_id: str, super_admin: bool = False):
    """
    Override dependency to return a lightweight user-like object with required attributes.
    Avoids mutating SQLAlchemy relationship attributes in tests.
    """
    def overridden_get_current_user():
        # Return a minimal object with id and optional role.name
        if super_admin:
            class DummyRole:
                name = "SUPER_ADMIN"
            class DummyUserSA:
                def __init__(self, uid: str):
                    self.id = uid
                    self.role = DummyRole()
            return DummyUserSA(user_id)
        else:
            class DummyUserRegular:
                def __init__(self, uid: str):
                    self.id = uid
                    self.role = None
            return DummyUserRegular(user_id)
    main.app.dependency_overrides[core.security.get_current_user] = overridden_get_current_user


def test_group_analytics_forbidden_for_non_member():
    # Create user and group; do not add membership
    user = _create_user("nonmember@example.com")
    group = _create_group(admin_id=None)

    # Override auth to return this user
    _override_current_user(user_id=str(user.id), super_admin=False)

    resp = client.get(f"/api/v1/analytics/group/{group.id}")
    assert resp.status_code == 403, resp.text
    assert resp.json().get("detail") in ["Not authorized to view this group's analytics"]


def test_group_analytics_allows_member():
    # Create user and group; add membership
    user = _create_user("member@example.com")
    group = _create_group(admin_id=None)
    _add_member(group_id=str(group.id), user_id=str(user.id))

    # Override auth to return this user
    _override_current_user(user_id=str(user.id), super_admin=False)

    resp = client.get(f"/api/v1/analytics/group/{group.id}")
    assert resp.status_code == 200, resp.text
    # Response is a dict of analytics; verify basic keys exist
    data = resp.json()
    assert data.get("group_id") == str(group.id)


def test_global_analytics_requires_super_admin():
    # Non-admin user
    user = _create_user("normal@example.com")
    _override_current_user(user_id=str(user.id), super_admin=False)

    resp_forbidden = client.get("/api/v1/analytics/global")
    assert resp_forbidden.status_code == 403, resp_forbidden.text
    assert resp_forbidden.json().get("detail") == "Super Admin access required"

    # Now override as SUPER_ADMIN
    # Ensure role exists for completeness (though we attach dummy role for check)
    _ensure_role("SUPER_ADMIN")
    _override_current_user(user_id=str(user.id), super_admin=True)

    resp_ok = client.get("/api/v1/analytics/global")
    assert resp_ok.status_code == 200, resp_ok.text
    data = resp_ok.json()
    # Verify required keys exist
    assert "total_users" in data and "total_groups" in data and "total_entries" in data


def test_rest_analytics_unauthenticated():
    """Test that REST analytics endpoints return 401 when no authentication."""
    # Clear any overrides to simulate unauthenticated state
    _clear_overrides()

    # Test group analytics unauthenticated
    group = _create_group()
    resp_group = client.get(f"/api/v1/analytics/group/{group.id}")
    assert resp_group.status_code == 401, resp_group.text

    # Test global analytics unauthenticated
    resp_global = client.get("/api/v1/analytics/global")
    assert resp_global.status_code == 401, resp_global.text


def _clear_overrides():
    """Helper to clear dependency overrides."""
    main.app.dependency_overrides.pop(core.security.get_current_user, None)
