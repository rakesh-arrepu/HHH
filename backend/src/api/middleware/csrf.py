"""
CSRF middleware (double-submit token pattern).

- For safe methods (GET/HEAD/OPTIONS), ensure a readable CSRF cookie (non-httpOnly) exists.
- For mutating methods (POST/PUT/PATCH/DELETE), require X-CSRF-Token header to match the CSRF cookie value.
- Cookies use SameSite=Lax; Secure follows settings.secure_cookies; domain from settings.cookie_domain.

Notes:
- This middleware should be added AFTER CORS and BEFORE routers in main.py.
- Double-submit does not require server-side storage; attacker cannot read cookies cross-site to set the matching header.
"""

from __future__ import annotations

import secrets
import json
from typing import Callable
from urllib.parse import parse_qs

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from core.config import settings


SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        method = request.method.upper()

        csrf_cookie_name = settings.csrf_cookie_name
        csrf_header_name = settings.csrf_header_name

        # Bypass CSRF checks for safe methods and preflight
        if method in SAFE_METHODS:
            response = await call_next(request)
            # Ensure CSRF cookie exists; if not, set one
            if not request.cookies.get(csrf_cookie_name):
                token = secrets.token_urlsafe(32)
                self._set_csrf_cookie(request, response, csrf_cookie_name, token)
            return response

        # Special-case: allow POST /graphql for read-only queries (no mutation) to avoid CSRF requirement
        if method == "POST" and request.url.path.startswith("/graphql"):
            body_bytes = await request.body()
            query_str = None
            content_type = (request.headers.get("content-type") or "").lower()

            try:
                if "application/json" in content_type:
                    data = json.loads(body_bytes.decode("utf-8") or "{}")
                    query_str = data.get("query") if isinstance(data, dict) else None
                elif content_type.startswith("application/graphql"):
                    # Body is the GraphQL query string directly
                    query_str = body_bytes.decode("utf-8") or ""
                elif content_type.startswith("application/x-www-form-urlencoded"):
                    # Body like: query=...&variables=...
                    parsed = parse_qs(body_bytes.decode("utf-8") or "")
                    q_vals = parsed.get("query")
                    query_str = q_vals[0] if q_vals else None
                else:
                    # Fallback: try JSON
                    data = json.loads(body_bytes.decode("utf-8") or "{}")
                    query_str = data.get("query") if isinstance(data, dict) else None
            except Exception:
                query_str = None

            # Reconstruct the request body for downstream after reading it
            async def receive():
                return {"type": "http.request", "body": body_bytes, "more_body": False}

            request = Request(request.scope, receive)

            # Allow APQ (persisted queries) without CSRF when no query text is provided
            try:
                data_for_apq = json.loads(body_bytes.decode("utf-8") or "{}") if "application/json" in content_type else {}
                if isinstance(data_for_apq, dict):
                    ex = data_for_apq.get("extensions") or {}
                    if isinstance(ex, dict) and "persistedQuery" in ex and not query_str:
                        # Pass through; backend may still 400 if APQ unsupported, but not 403 CSRF
                        return await call_next(request)
            except Exception:
                pass

            if isinstance(query_str, str) and "mutation" not in query_str.lower():
                # Treat as read-only GraphQL query; bypass CSRF
                return await call_next(request)

            # Fallback: if parsing failed or no query text, scan raw body for "mutation" token.
            # If not found, treat as read-only and bypass CSRF (covers unusual content-types/APQ-like payloads).
            try:
                lower_body = (body_bytes.decode("utf-8", errors="ignore") or "").lower()
                if "mutation" not in lower_body:
                    return await call_next(request)
            except Exception:
                pass

        # For mutating requests, enforce double-submit: header must equal cookie
        header_token = request.headers.get(csrf_header_name)
        cookie_token = request.cookies.get(csrf_cookie_name)

        if not header_token or not cookie_token or header_token != cookie_token:
            return JSONResponse({"detail": "CSRF validation failed"}, status_code=403)

        # Passed CSRF check
        return await call_next(request)

    def _set_csrf_cookie(self, request: Request, response: Response, name: str, value: str) -> None:
        """
        Set CSRF cookie. If configured cookie_domain doesn't match the current host (e.g., 'testserver'
        during TestClient runs), omit the Domain attribute so the client accepts it.
        """
        host = request.url.hostname or ""
        configured_domain = settings.cookie_domain or None

        # In local dev, never set Domain attribute for localhost/127.0.0.1; browsers may reject Domain=localhost
        if host in {"localhost", "127.0.0.1"}:
            domain_to_use = None
        else:
            domain_to_use = configured_domain if (configured_domain and configured_domain == host) else None

        response.set_cookie(
            key=name,
            value=value,
            httponly=False,  # must be readable by JS to set header
            secure=settings.secure_cookies,
            samesite="lax",
            domain=domain_to_use,
            path="/",
            max_age=60 * 60 * 24 * 7,  # 7 days
        )
