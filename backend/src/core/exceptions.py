from typing import Any, Dict, Optional
from datetime import datetime, timezone
from fastapi import Request
from fastapi.responses import JSONResponse
from graphql.error import GraphQLError
import logging
from contextvars import ContextVar

# Per-request correlation id (set by middleware)
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")

# Structured logger for GraphQL error formatting
logger = logging.getLogger("hhh.graphql")

# ---- Domain Exceptions ----
class AppError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400,
    ):
        self.message = message
        self.code = code or "ERR_BAD_REQUEST"
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized", *, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="ERR_UNAUTHORIZED", details=details, status_code=401)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden", *, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="ERR_FORBIDDEN", details=details, status_code=403)


class NotFoundError(AppError):
    def __init__(self, message: str = "Not Found", *, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="ERR_NOT_FOUND", details=details, status_code=404)


class ValidationError(AppError):
    def __init__(self, message: str = "Validation error", *, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="ERR_VALIDATION", details=details, status_code=422)


# ---- Helpers ----
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_corr_id_from_request(request: Optional[Request]) -> Optional[str]:
    try:
        return getattr(getattr(request, "state", None), "correlation_id", None)
    except Exception:
        return None


def build_error_payload(
    message: str,
    *,
    code: str,
    request: Optional[Request] = None,
    path: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Standardized error envelope.

    Schema (top-level):
      { code, message, details?, correlationId?, path?, timestamp }

    For backward-compatibility with existing clients/tests, we also include:
      - detail (FastAPI default)
      - error { code, message, meta } (legacy structured object)
    """
    corr_id = _get_corr_id_from_request(request) or correlation_id_var.get() or None
    resolved_path = path
    try:
        if not resolved_path and request is not None:
            resolved_path = str(request.url.path)
    except Exception:
        pass

    payload: Dict[str, Any] = {
        "code": code,
        "message": message,
        "details": details or {},
        "correlationId": corr_id,
        "path": resolved_path,
        "timestamp": _now_iso(),
        # Legacy fields for compatibility:
        "detail": message,
        "error": {
            "code": code,
            "message": message,
            "meta": details or {},
        },
    }
    return payload


def error_response(
    status_code: int,
    message: str,
    *,
    code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
    path: Optional[str] = None,
) -> JSONResponse:
    """
    Standardized error response for REST endpoints.
    """
    payload = build_error_payload(
        message,
        code=code or f"ERR_{status_code}",
        details=details,
        request=request,
        path=path,
    )
    return JSONResponse(status_code=status_code, content=payload)

# ---- GraphQL helpers (version-safe) ----
def gql_error(
    message: str,
    code: str,
    details: Optional[Dict[str, Any]] = None,
    *,
    path: Optional[str] = None,
) -> GraphQLError:
    """
    Build a GraphQL error with standardized extensions.
    - code: machine-readable error code (e.g., ERR_UNAUTHORIZED)
    - details: optional dict with additional data (safe to expose)
    - path: optional field path string (e.g., 'dailyProgress'); included in extensions for client tests
    """
    extensions = {
        "code": code,
        "details": details or {},
        "correlationId": correlation_id_var.get() or None,
        "timestamp": _now_iso(),
        "path": path,
    }
    return GraphQLError(message, extensions=extensions)


# ---- GraphQL Error Formatter ----
def _infer_code_from_exception(exc: Optional[BaseException]) -> str:
    if isinstance(exc, UnauthorizedError):
        return "ERR_UNAUTHORIZED"
    if isinstance(exc, ForbiddenError):
        return "ERR_FORBIDDEN"
    if isinstance(exc, NotFoundError):
        return "ERR_NOT_FOUND"
    if isinstance(exc, ValidationError):
        return "ERR_VALIDATION"
    if isinstance(exc, AppError):
        try:
            return getattr(exc, "code", "ERR_GRAPHQL") or "ERR_GRAPHQL"
        except Exception:
            return "ERR_GRAPHQL"
    # Fallback generic GraphQL error
    return "ERR_GRAPHQL"


def graphql_error_formatter(error: GraphQLError) -> Dict[str, Any]:
    """
    Strawberry-compatible error formatter that returns a GraphQL-compliant shape
    plus a standardized envelope inside 'extensions'.
    """
    original = getattr(error, "original_error", None)
    message = str(original) if original is not None else error.message
    code = _infer_code_from_exception(original)
    details: Dict[str, Any] = {}

    if hasattr(original, "details") and isinstance(getattr(original, "details"), dict):
        details = getattr(original, "details")  # type: ignore[assignment]

    extensions = {
        "code": code,
        "details": details,
        "correlationId": correlation_id_var.get() or None,
        "timestamp": _now_iso(),
        "path": getattr(error, "path", None),
    }

    # Log GraphQL errors with correlation context for observability
    try:
        # AppError family -> warning; unexpected -> error
        is_expected = isinstance(original, AppError)
        log_msg = (
            f"GraphQLError code={code} path={getattr(error, 'path', None)} "
            f"corrId={correlation_id_var.get() or None} message={message}"
        )
        if is_expected:
            logger.warning(log_msg)
        else:
            logger.error(log_msg)
    except Exception:
        # Never fail formatter due to logging issues
        pass

    return {
        "message": message,
        "locations": error.locations,  # type: ignore[attr-defined]
        "path": error.path,  # type: ignore[attr-defined]
        "extensions": extensions,
    }
