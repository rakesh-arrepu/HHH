"""
Script to update the existing super admin user(s) in the Users table,
forcing both email and name to be lower case (and stripping whitespace).

Usage:
    python backend/scripts/lowercase_super_admin.py

Requirements:
    - backend/.env set up correctly
    - Dependencies: pip install -r backend/requirements/dev.txt
"""

import sys
import os

# Setup path so core.*, models.*, etc. are resolvable
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_PATH = os.path.join(REPO_ROOT, "backend", "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from core.database import SessionLocal
from models.role import Role
from models.user import User

def normalize(val: str) -> str:
    return val.strip().lower()

def main():
    session = SessionLocal()

    admin_role = session.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        print("No 'admin' role found. Exiting.")
        return

    admin_users = session.query(User).filter(User.role_id == admin_role.id).all()
    if not admin_users:
        print("No users with 'admin' role found.")
        return

    for user in admin_users:
        orig_email = getattr(user, "email")
        orig_name = getattr(user, "name")
        new_email = normalize(orig_email)
        new_name = normalize(orig_name)
        setattr(user, "email", new_email)
        setattr(user, "name", new_name)
        print(f"Updated user: {orig_email} => {new_email}, {orig_name} => {new_name}")

    session.commit()
    print(f"Updated {len(admin_users)} super admin user(s) to lower case.")

    session.close()

if __name__ == "__main__":
    main()
