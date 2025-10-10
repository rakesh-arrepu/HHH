from enum import Enum as PyEnum
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from core.database import Base


class NotificationType(PyEnum):
  INCOMPLETE_DAY = "incomplete_day"
  STREAK_MILESTONE = "streak_milestone"
  ADMIN_ACTION = "admin_action"
  MODERATION = "moderation"


class Notification(Base):
  __tablename__ = "notifications"

  id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
  user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

  type = Column(Enum(NotificationType), nullable=False)
  title = Column(String(200), nullable=False)
  message = Column(Text, nullable=False)
  is_read = Column(Boolean, nullable=False, default=False)

  created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

  # Relationships
  user = relationship("User", backref="notifications")
