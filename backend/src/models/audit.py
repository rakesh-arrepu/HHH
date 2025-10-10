from uuid import uuid4
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func

from core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(36), nullable=False, index=True)
    meta = Column("metadata", JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
