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


app = FastAPI(title=settings.app_name, debug=settings.debug)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


@app.on_event("startup")
def on_startup():
    # For developer convenience: create tables if they don't exist (SQLite/local dev).
    # In production, use Alembic migrations.
    Base.metadata.create_all(bind=engine)


# Routers
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["auth"])


@app.get("/")
def root():
    return {"message": "daily-tracker backend"}
