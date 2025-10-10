from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from core.database import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    timezone = Column(String(50), nullable=False, default="Asia/Kolkata")

    admin_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    admin = relationship("User", backref="admin_groups", foreign_keys=[admin_id])

    # Define backrefs when related models are present:
    # members = relationship("GroupMember", back_populates="group")
    # entries = relationship("SectionEntry", back_populates="group")
