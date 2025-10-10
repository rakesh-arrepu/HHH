# Make SQLAlchemy Base and all models importable for Alembic autogeneration
from core.database import Base

# Import models so Alembic can discover them via Base.metadata
from .role import Role  # noqa: F401
from .user import User  # noqa: F401
from .group import Group  # noqa: F401
from .group_member import GroupMember  # noqa: F401
from .entry import SectionEntry  # noqa: F401
from .notification import Notification  # noqa: F401
from .audit import AuditLog  # noqa: F401
from .backup_log import BackupLog  # noqa: F401

__all__ = [
    "Base",
    "Role",
    "User",
    "Group",
    "GroupMember",
    "SectionEntry",
    "Notification",
    "AuditLog",
    "BackupLog",
]
