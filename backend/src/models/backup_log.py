from uuid import uuid4
from sqlalchemy import Column, String, DateTime, BigInteger, Enum as SAEnum
from sqlalchemy.sql import func

from core.database import Base


class BackupStatus(str):
    SUCCESS = "success"
    FAILED = "failed"


class BackupLog(Base):
    __tablename__ = "backup_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    backup_file = Column(String(255), nullable=False)
    backup_size = Column(BigInteger, nullable=False)
    status = Column(SAEnum(BackupStatus.SUCCESS, BackupStatus.FAILED, name="backup_status"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
