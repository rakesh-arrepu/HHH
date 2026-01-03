"""
Script to ensure a super admin (system administrator) exists.

- Creates a Role 'admin' if it does not exist.
- Prompts for email, name, and password and creates a User with the admin role if none exists.
- Will not overwrite existing super admin—idempotent and safe.

Usage:
    python backend/scripts/create_super_admin.py

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

from core.database import SessionLocal, Base, engine
from models.role import Role
from models.user import User
from core.security import get_password_hash

def normalize_email(email: str) -> str:
    return email.strip().lower()

def main():
    session = SessionLocal()

    admin_role = session.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Super administrator with full privileges.")
        session.add(admin_role)
        session.commit()
        print("Created 'admin' role.")

    admin_user = session.query(User).filter(User.role_id == admin_role.id).first()
    if admin_user:
        print(f"A user with role 'admin' already exists: {admin_user.email}")
    else:
        print("No super admin user found. Creating one now.")
        email = "rakesh.arrepu@gmail.com"
        email_n = normalize_email(email)
        name = "super_rocky"
        password = "Super@123456"
        password_hash = get_password_hash(password)
        new_admin = User(
            email=email_n,
            name=name,
            password_hash=password_hash,
            role_id=admin_role.id,
        )
        session.add(new_admin)
        session.commit()
        print(f"Super admin user created with email: {email_n}")

    session.close()

if __name__ == "__main__":
    main()
