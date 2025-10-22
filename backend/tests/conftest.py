import os
import sys
from typing import Generator, Tuple

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend/src is on sys.path so imports like "core.*" and "models.*" work in tests
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from core.database import Base  # type: ignore  # noqa: E402
from models.user import User  # type: ignore  # noqa: E402
from models.group import Group  # type: ignore  # noqa: E402
from models.entry import SectionEntry  # type: ignore  # noqa: E402


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """
    Provide a fresh SQLite in-memory DB session per test function.
    Creates all metadata on a dedicated engine; does not rely on application engine.
    """
    engine = create_engine("sqlite:///:memory:", future=True, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

    # Create tables for all imported models
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def user_factory(db_session):
    def _create_user(email: str = "user@example.com", name: str = "Test User", password_hash: str = "x") -> User:
        u = User(email=email, name=name, password_hash=password_hash)
        db_session.add(u)
        db_session.commit()
        db_session.refresh(u)
        return u

    return _create_user


@pytest.fixture()
def group_factory(db_session):
    def _create_group(name: str = "Group A", description: str = "Desc", admin_id: str | None = None) -> Group:
        g = Group(name=name, description=description, admin_id=admin_id)
        db_session.add(g)
        db_session.commit()
        db_session.refresh(g)
        return g

    return _create_group


@pytest.fixture()
def user_group(db_session, user_factory, group_factory) -> Tuple[str, str]:
    """
    Convenience fixture returning (user_id, group_id) for use in service tests.
    """
    user = user_factory()
    group = group_factory(admin_id=user.id)
    return user.id, group.id
