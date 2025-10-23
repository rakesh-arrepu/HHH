from datetime import datetime, timezone
from typing import Any, Optional, Tuple, cast

from core.security import create_access_token, get_password_hash, verify_password
from models.user import User
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


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
    import logging
    email_n = normalize_email(email)
    logging.warning(f"[AUTH_DEBUG] Called with email='{email}', normalized='{email_n}'")
    user = get_user_by_email(db, email_n)
    logging.warning(f"[AUTH_DEBUG] User found: {user is not None}, DB user email: {getattr(user, 'email', None)}")
    if not user:
        logging.error("[AUTH_DEBUG] No user found for normalized email.")
        raise ValueError("Invalid credentials")
    pw_check = verify_password(password, cast(str, user.password_hash))
    logging.warning(f"[AUTH_DEBUG] Password hash check result for email='{email_n}': {pw_check}")
    if not pw_check:
        logging.error("[AUTH_DEBUG] Password verification failed.")
        raise ValueError("Invalid credentials")

    # Update last_login
    cast(Any, user).last_login = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create access token (JWT)
    token = create_access_token({"sub": user.id, "email": user.email})
    logging.warning(f"[AUTH_DEBUG] Login successful for {email_n}")
    return user, token
