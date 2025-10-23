"""
Script to print all rows from every table in the project database using SQLAlchemy and project settings.

Usage:
    python backend/scripts/print_all_tables.py

Requirements:
    - backend/.env set up correctly (see .env.example)
    - All dependencies installed (pip install -r backend/requirements/dev.txt)

Tables covered: AuditLog, BackupLog, SectionEntry, Group, GroupMember, Notification, Role, User
"""

import sys
import os

# Fix sys.path so both 'src' and 'models' are resolvable regardless of CWD
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_PATH = os.path.join(REPO_ROOT, "backend", "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from core.database import SessionLocal  # Now resolved as backend/src/core/database.py

from models.audit import AuditLog
from models.backup_log import BackupLog
from models.entry import SectionEntry
from models.group import Group
from models.group_member import GroupMember
from models.notification import Notification
from models.role import Role
from models.user import User

MODELS = [
    AuditLog,
    BackupLog,
    SectionEntry,
    Group,
    GroupMember,
    Notification,
    Role,
    User,
]

def row_as_dict(row):
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}

def main():
    session = SessionLocal()
    for model in MODELS:
        print(f"\nTable: {model.__tablename__}")
        try:
            rows = session.query(model).all()
            if not rows:
                print("  (No rows)")
            else:
                for row in rows:
                    print("  ", row_as_dict(row))
        except Exception as exc:
            print(f"  Error querying table {model.__tablename__}: {exc}")
    session.close()

if __name__ == "__main__":
    main()
