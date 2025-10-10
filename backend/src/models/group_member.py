from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from core.database import Base


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    group_id = Column(String(36), ForeignKey("groups.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    day_streak = Column(Integer, nullable=False, default=0)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    group = relationship("Group", backref="members")
    user = relationship("User", backref="group_memberships")


# Partial unique index to prevent duplicate active memberships (PostgreSQL only)
# For SQLite (dev) this will simply be ignored safely.
try:
    from sqlalchemy.dialects.postgresql import dialect  # type: ignore # noqa: F401

    Index(
        "uq_active_group_members",
        GroupMember.group_id,
        GroupMember.user_id,
        unique=True,
        postgresql_where=GroupMember.deleted_at.is_(None),
    )
except Exception:
    # Non-Postgres dialects won't use postgresql_where
    pass
