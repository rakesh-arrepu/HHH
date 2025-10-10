from enum import Enum as PyEnum
from uuid import uuid4
from sqlalchemy import (
    Column,
    String,
    Text,
    Date,
    DateTime,
    Integer,
    Boolean,
    ForeignKey,
    Enum,
    Index,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from core.database import Base


class SectionType(PyEnum):
    Health = "Health"
    Happiness = "Happiness"
    Hela = "Hela"  # Money


class SectionEntry(Base):
    __tablename__ = "section_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    group_id = Column(String(36), ForeignKey("groups.id"), nullable=False, index=True)

    section_type = Column(Enum(SectionType), nullable=False)
    content = Column(Text, nullable=False)
    entry_date = Column(Date, nullable=False)

    edit_count = Column(Integer, nullable=False, default=0)
    is_flagged = Column(Boolean, nullable=False, default=False)
    flagged_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", backref="entries")
    group = relationship("Group", backref="entries")


# Partial unique index to enforce one active entry per section per day (PostgreSQL only)
# In dev (SQLite), this condition is ignored; enforce at service layer.
try:
    from sqlalchemy.dialects.postgresql import dialect  # type: ignore # noqa: F401

    Index(
        "uq_active_daily_section_entry",
        SectionEntry.user_id,
        SectionEntry.group_id,
        SectionEntry.section_type,
        SectionEntry.entry_date,
        unique=True,
        postgresql_where=SectionEntry.deleted_at.is_(None),
    )
except Exception:
    # Non-Postgres dialects won't use postgresql_where
    pass
