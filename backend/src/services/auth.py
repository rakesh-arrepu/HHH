from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from core.security import get_password_hash, verify_password, create_access_token
from models.user import User


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == normalize_email(email)).first()


def create_user(db: Session, email: str, password: str, name: str) -> User:
    email_n = normalize_email(email)
    existing = get_user_by_email(db, email_n)
    if existing:
        raise ValueError("Email already registered")

    user = User(
        email=email_n,
        password_hash=get_password_hash(password),
        name=name.strip(),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Could not create user (integrity error)") from e
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Tuple[User, str]:
    email_n = normalize_email(email)
    user = get_user_by_email(db, email_n)
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Invalid credentials")

    # Update last_login
    user.last_login = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create access token (JWT)
    token = create_access_token({"sub": user.id, "email": user.email})
    return user, token
