from uuid import uuid4
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)

    totp_secret = Column(String(255), nullable=True)
    is_2fa_enabled = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    role = relationship("Role", back_populates="users")

    # Optionally define these when corresponding models exist
    # groups_admin = relationship("Group", back_populates="admin", foreign_keys="Group.admin_id")
    # group_memberships = relationship("GroupMember", back_populates="user")
    # entries = relationship("SectionEntry", back_populates="user")
    # notifications = relationship("Notification", back_populates="user")
