import os
import sys

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
from strawberry.fastapi import GraphQLRouter  # type: ignore  # noqa: E402
from api.graphql.schema import schema  # type: ignore  # noqa: E402
from api.middleware.csrf import CSRFMiddleware  # type: ignore  # noqa: E402


app = FastAPI(title=settings.app_name, debug=settings.debug)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

app.add_middleware(CSRFMiddleware)


@app.on_event("startup")
def on_startup():
    # For developer convenience: create tables if they don't exist (SQLite/local dev).
    # In production, use Alembic migrations.
    Base.metadata.create_all(bind=engine)


# Routers
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(roles_router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(backup_router, prefix="/api/v1/backups", tags=["backups"])


@app.get("/")
def root():
    return {"message": "daily-tracker backend"}
