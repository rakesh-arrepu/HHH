# SQLAlchemy database setup (synchronous)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from typing import Generator
from .config import settings


# Use SQLite check_same_thread flag for local dev
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, echo=settings.debug, future=True, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

Base = declarative_base()

# Ensure all models are registered for create_all in dev/tests
from models.user import User
from models.group import Group
from models.entry import SectionEntry
from models.role import Role
from models.group_member import GroupMember
from models.notification import Notification
from models.backup_log import BackupLog
from models.audit import AuditLog


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
