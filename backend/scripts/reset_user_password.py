"""
Script to reset the password for any user (typically used to recover admin access).

Usage:
    python backend/scripts/reset_user_password.py

Requires:
    - backend/.env set up correctly
    - pip install -r backend/requirements/dev.txt
"""

import sys
import os

# Setup path so core.*, models.*, etc. are resolvable
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_PATH = os.path.join(REPO_ROOT, "backend", "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from core.database import SessionLocal
from models.user import User
from core.security import get_password_hash

def normalize_email(email: str) -> str:
    return email.strip().lower()

def main():
    session = SessionLocal()
    email = input("Enter email of the user to reset password: ")
    email_n = normalize_email(email)
    user = session.query(User).filter(User.email == email_n).first()
    if not user:
        print(f"No user found with email: {email_n}")
        return
    password = input("Enter new password: ").strip()
    user.password_hash = get_password_hash(password) # type: ignore
    session.commit()
    print(f"Password reset for user {email_n}")
    session.close()

if __name__ == "__main__":
    main()
