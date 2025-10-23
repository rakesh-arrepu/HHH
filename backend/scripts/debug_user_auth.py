"""
Script to debug user authentication.
Checks:
1. Whether the user (by normalized email) exists and prints fields.
2. Validates the provided password against the stored hash (using verify_password).
3. Prints status for 'deleted_at' and other blockers.

Usage:
    python backend/scripts/debug_user_auth.py

Requirements:
    - backend/.env correctly set
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
from core.security import verify_password

def normalize_email(email: str) -> str:
    return email.strip().lower()

def main():
    session = SessionLocal()
    email = input("Enter user's email: ")
    password = input("Enter user's password: ")
    email_n = normalize_email(email)
    user = session.query(User).filter(User.email == email_n).first()
    if not user:
        print(f"User with normalized email '{email_n}' not found.")
        return

    print("--- User Info ---")
    print(f"ID: {user.id}")
    print(f"Email: {user.email}")
    print(f"Name: {user.name}")
    print(f"Role ID: {user.role_id}")
    print(f"Deleted At: {user.deleted_at}")
    print(f"Password Hash: {user.password_hash}")
    print(f"Password Hash Length: {len(user.password_hash) if user.password_hash else 'None'}") # type: ignore

    # Try password check
    result = verify_password(password, user.password_hash) # pyright: ignore[reportArgumentType]
    print(f"\nverify_password('{password}', user.password_hash) => {result}")

    session.close()

if __name__ == "__main__":
    main()
