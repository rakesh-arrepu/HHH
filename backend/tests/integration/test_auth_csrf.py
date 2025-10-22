import os
import sys
import uuid
from typing import Dict, Any

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Use a file-based SQLite DB for integration tests to avoid in-memory connection issues
os.environ["DATABASE_URL"] = "sqlite:///./test_app.db"

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402

from core.database import Base, engine

Base.metadata.create_all(bind=engine)

client = TestClient(main.app)


def _csrf_token() -> str | None:
    # Hitting a safe endpoint should ensure CSRF cookie exists (CSRFMiddleware behavior for safe methods)
    r = client.get("/api/v1/auth/health")
    assert r.status_code == 200
    return client.cookies.get("hhh_csrf")


def test_register_requires_csrf() -> None:
    # Without CSRF header, mutating request should be rejected
    payload: Dict[str, Any] = {
        "email": f"user_{uuid.uuid4().hex[:8]}@example.com",
        "password": "password123",
        "name": "Test User",
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 403
    assert resp.json().get("detail") == "CSRF validation failed"


def test_register_sets_cookies_with_csrf() -> None:
    token = _csrf_token()
    assert token is not None

    payload: Dict[str, Any] = {
        "email": f"user_{uuid.uuid4().hex[:8]}@example.com",
        "password": "password123",
        "name": "Test User",
    }
    resp = client.post(
        "/api/v1/auth/register",
        json=payload,
        headers={"X-CSRF-Token": token},
    )
    # Expect "Created"
    assert resp.status_code == 201, resp.text
    # Should include both cookie names in set-cookie header (as per our security.py implementation)
    set_cookie = resp.headers.get("set-cookie", "")
    assert "hhh_at" in set_cookie
    assert "hhh_rt" in set_cookie


def test_graphql_csrf_enforced() -> None:
    # Without header -> 403 from middleware
    gql_mutation = {"query": 'mutation { deleteEntry(id: "fake-id") }'}
    resp_forbidden = client.post("/graphql", json=gql_mutation)
    assert resp_forbidden.status_code == 403
    assert resp_forbidden.json().get("detail") == "CSRF validation failed"

    # With header -> not blocked by CSRF (might still error at GraphQL/resolver layer, but not 403)
    token = _csrf_token()
    assert token is not None
    resp_allowed = client.post("/graphql", json=gql_mutation, headers={"X-CSRF-Token": token})
    assert resp_allowed.status_code != 403
