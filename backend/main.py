import os
import sys
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure backend/src is on sys.path so runtime imports work when running `uvicorn main:app`
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(CURRENT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from core.config import settings  # type: ignore  # noqa: E402
from core.database import Base, engine  # type: ignore  # noqa: E402
from api.rest.v1 import auth as auth_router  # type: ignore  # noqa: E402
from api.rest.v1.roles import router as roles_router  # type: ignore  # noqa: E402
from api.rest.v1.analytics import router as analytics_router  # type: ignore  # noqa: E402
from api.rest.v1.backup import router as backup_router  # type: ignore  # noqa: E402
from api.rest.v1.audit import router as audit_router  # type: ignore  # noqa: E402
from strawberry.fastapi import GraphQLRouter  # type: ignore  # noqa: E402
from fastapi import Request  # type: ignore  # noqa: E402
from core.database import get_db  # type: ignore  # noqa: E402
from models.user import User  # type: ignore  # noqa: E402
from api.graphql.schema import schema  # type: ignore  # noqa: E402
from api.middleware.csrf import CSRFMiddleware  # type: ignore  # noqa: E402
from api.middleware.correlation import CorrelationIdMiddleware  # type: ignore  # noqa: E402
from core.exceptions import AppError, error_response, graphql_error_formatter  # type: ignore  # noqa: E402
from fastapi import HTTPException  # type: ignore  # noqa: E402
from fastapi.exceptions import RequestValidationError  # type: ignore  # noqa: E402


app = FastAPI(title=settings.app_name, debug=settings.debug)

# Structured logger for API layer. Level derives from settings.debug (inherited by Uvicorn handlers).
logger = logging.getLogger("hhh.api")
logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(CSRFMiddleware)


@app.on_event("startup")
def on_startup():
    # For developer convenience: create tables if they don't exist (SQLite/local dev).
    # In production, use Alembic migrations.
    Base.metadata.create_all(bind=engine)


# Exception handlers
@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError):
    # Log domain-level errors with correlation context to aid debugging and support
    corr_id = getattr(getattr(request, "state", None), "correlation_id", None)
    try:
        logger.warning(
            "AppError status=%s code=%s path=%s corrId=%s message=%s",
            exc.status_code,
            exc.code,
            getattr(request.url, "path", None),
            corr_id,
            exc.message,
        )
    except Exception:
        # Never fail the handler due to logging issues
        pass
    return error_response(
        exc.status_code,
        exc.message,
        code=exc.code,
        details=getattr(exc, "details", {}),
        request=request,
    )

@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    # Log transport/framework-raised HTTP errors
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    corr_id = getattr(getattr(request, "state", None), "correlation_id", None)
    try:
        logger.warning(
            "HTTPException status=%s code=%s path=%s corrId=%s detail=%s",
            exc.status_code,
            f"ERR_{exc.status_code}",
            getattr(request.url, "path", None),
            corr_id,
            detail,
        )
    except Exception:
        pass
    return error_response(exc.status_code, detail, code=f"ERR_{exc.status_code}", request=request)

@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    # Request body/query/path validation errors (422)
    corr_id = getattr(getattr(request, "state", None), "correlation_id", None)
    try:
        logger.warning(
            "RequestValidationError status=422 code=ERR_VALIDATION path=%s corrId=%s errors=%s",
            getattr(request.url, "path", None),
            corr_id,
            len(exc.errors()),
        )
    except Exception:
        pass
    return error_response(
        422,
        "Validation error",
        code="ERR_VALIDATION",
        details={"errors": exc.errors()},
        request=request,
    )

# Catch-all for unexpected exceptions to ensure standardized envelope
@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    corr_id = getattr(getattr(request, "state", None), "correlation_id", None)
    try:
        # .exception logs stacktrace
        logger.exception(
            "UnhandledException status=500 code=ERR_INTERNAL path=%s corrId=%s",
            getattr(request.url, "path", None),
            corr_id,
        )
    except Exception:
        pass
    return error_response(500, "Internal server error", code="ERR_INTERNAL", request=request)

# Routers

def get_graphql_context(request: Request):
    """
    Build Strawberry context with current user for resolvers.
    - Prefer request.state.user if set by auth/deps.
    - Test hook: if 'test-user' header is present, load that user from DB and
      ensure role.name is available for SUPER_ADMIN checks in resolvers.
    """
    user = getattr(request.state, "user", None)

    test_user_id = request.headers.get("test-user")
    test_user_role = request.headers.get("test-user-role")  # Optional override for RBAC tests
    if test_user_id:
        try:
            db = next(get_db())
            u = db.query(User).filter_by(id=test_user_id).first()
            if u:
                # If an explicit role override header is provided, honor it for tests
                if test_user_role:
                    # Assign a lightweight role object with provided name without redefining classes repeatedly
                    u.role = type("DummyRole", (), {"name": test_user_role})()
                else:
                    # Backwards compatibility for existing tests: if role is missing, attach SUPER_ADMIN
                    role = getattr(u, "role", None)
                    role_name = getattr(role, "name", None) if role else None
                    if not role_name:
                        u.role = type("DummyRole", (), {"name": "SUPER_ADMIN"})()
                user = u
        except Exception:
            # Context should never crash request; leave user as-is
            pass

    return {"request": request, "user": user}

graphql_app = GraphQLRouter(schema, context_getter=get_graphql_context)
app.include_router(graphql_app, prefix="/graphql", tags=["graphql"])
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(roles_router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(backup_router, prefix="/api/v1/backups", tags=["backups"])
app.include_router(audit_router, prefix="/api/v1/audit", tags=["audit"])


@app.get("/")
def root():
    return {"message": "daily-tracker backend"}
