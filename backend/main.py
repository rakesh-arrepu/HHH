from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import Optional, Literal, cast
import os
import re
import logging
from fastapi import FastAPI, Depends, HTTPException, Response, Cookie, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

from database import engine, get_db, Base
from models import User, Group, GroupMember, Entry, ActivityType, HealthActivity, UserActivityFavorite # type: ignore
from auth import hash_password, verify_password, create_session_token, verify_session_token, create_password_reset_token, verify_password_reset_token
from email_service import (
    send_password_reset_email,
    is_email_configured,
    send_welcome_email,
    send_member_added_email_to_member,
    send_member_added_email_to_owner,
    send_ownership_transfer_email_to_new_owner,
    send_ownership_transfer_email_to_previous_owner
)

# Configure logging
logger = logging.getLogger(__name__)


# ============== Error Response Helper ==============

def api_error(status_code: int, detail: str, code: str | None = None) -> HTTPException:
    """Create an HTTPException with optional error code for frontend handling."""
    error_detail = {"detail": detail}
    if code:
        error_detail["code"] = code
    return HTTPException(status_code=status_code, detail=detail)


def verify_group_owner(db: Session, group_id: int, user_id: int) -> bool:
    """Verify if user is the owner of the specified group."""
    group = db.query(Group).filter(Group.id == group_id).first()
    return group is not None and group.owner_id == user_id


def set_session_cookie(response: Response, token: str) -> None:
    """
    Set session cookie with appropriate attributes for cross-site requests.

    For production (cross-site), we need:
    - SameSite=None (allow cross-site)
    - Secure=true (required with SameSite=None)
    - HttpOnly (security - no JS access)
    - Path=/ (available across entire domain)
    """
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite=COOKIE_SAMESITE,
        secure=COOKIE_SECURE,
        max_age=60 * 60 * 24 * 7,  # 7 days
        path="/"
    )


# Create tables
Base.metadata.create_all(bind=engine)

# ============== Seed Activity Types ==============

ACTIVITY_TYPES_SEED = [
    # Cardio (category: cardio)
    {"name": "Walking", "category": "cardio", "icon": "footprints", "color": "emerald", "met_value": 3.5, "default_duration": 30, "display_order": 1},
    {"name": "Running", "category": "cardio", "icon": "zap", "color": "red", "met_value": 9.8, "default_duration": 30, "display_order": 2},
    {"name": "Jogging", "category": "cardio", "icon": "activity", "color": "orange", "met_value": 7.0, "default_duration": 30, "display_order": 3},
    {"name": "Cycling", "category": "cardio", "icon": "bike", "color": "blue", "met_value": 7.5, "default_duration": 30, "display_order": 4},
    {"name": "Swimming", "category": "cardio", "icon": "waves", "color": "cyan", "met_value": 8.0, "default_duration": 30, "display_order": 5},
    {"name": "Jump Rope", "category": "cardio", "icon": "move", "color": "pink", "met_value": 12.0, "default_duration": 15, "display_order": 6},
    {"name": "Stair Climbing", "category": "cardio", "icon": "trending-up", "color": "purple", "met_value": 8.0, "default_duration": 20, "display_order": 7},
    {"name": "Elliptical", "category": "cardio", "icon": "circle", "color": "teal", "met_value": 5.0, "default_duration": 30, "display_order": 8},
    {"name": "Rowing", "category": "cardio", "icon": "ship", "color": "indigo", "met_value": 7.0, "default_duration": 20, "display_order": 9},
    {"name": "Dancing", "category": "cardio", "icon": "music", "color": "fuchsia", "met_value": 5.5, "default_duration": 30, "display_order": 10},

    # Sports (category: sports)
    {"name": "Cricket", "category": "sports", "icon": "circle-dot", "color": "yellow", "met_value": 5.0, "default_duration": 60, "display_order": 11},
    {"name": "Badminton", "category": "sports", "icon": "circle-dot", "color": "lime", "met_value": 5.5, "default_duration": 45, "display_order": 12},
    {"name": "Tennis", "category": "sports", "icon": "circle", "color": "green", "met_value": 7.0, "default_duration": 60, "display_order": 13},
    {"name": "Football", "category": "sports", "icon": "circle", "color": "emerald", "met_value": 7.0, "default_duration": 60, "display_order": 14},
    {"name": "Basketball", "category": "sports", "icon": "circle", "color": "orange", "met_value": 6.5, "default_duration": 45, "display_order": 15},
    {"name": "Volleyball", "category": "sports", "icon": "circle", "color": "blue", "met_value": 4.0, "default_duration": 45, "display_order": 16},
    {"name": "Table Tennis", "category": "sports", "icon": "circle-dot", "color": "red", "met_value": 4.0, "default_duration": 30, "display_order": 17},
    {"name": "Golf", "category": "sports", "icon": "flag", "color": "green", "met_value": 4.5, "default_duration": 120, "display_order": 18},
    {"name": "Hockey", "category": "sports", "icon": "goal", "color": "blue", "met_value": 8.0, "default_duration": 60, "display_order": 19},
    {"name": "Squash", "category": "sports", "icon": "square", "color": "purple", "met_value": 7.5, "default_duration": 45, "display_order": 20},
    {"name": "Rugby", "category": "sports", "icon": "shield", "color": "red", "met_value": 8.5, "default_duration": 60, "display_order": 21},
    {"name": "Baseball", "category": "sports", "icon": "circle", "color": "white", "met_value": 5.0, "default_duration": 90, "display_order": 22},

    # Strength & Fitness (category: strength)
    {"name": "Gym Workout", "category": "strength", "icon": "dumbbell", "color": "purple", "met_value": 6.0, "default_duration": 45, "display_order": 23},
    {"name": "Weight Training", "category": "strength", "icon": "dumbbell", "color": "slate", "met_value": 5.0, "default_duration": 45, "display_order": 24},
    {"name": "HIIT", "category": "strength", "icon": "flame", "color": "red", "met_value": 8.0, "default_duration": 30, "display_order": 25},
    {"name": "CrossFit", "category": "strength", "icon": "x", "color": "orange", "met_value": 8.0, "default_duration": 45, "display_order": 26},
    {"name": "Calisthenics", "category": "strength", "icon": "user", "color": "blue", "met_value": 5.0, "default_duration": 30, "display_order": 27},
    {"name": "Kettlebell", "category": "strength", "icon": "dumbbell", "color": "amber", "met_value": 6.0, "default_duration": 30, "display_order": 28},
    {"name": "Circuit Training", "category": "strength", "icon": "repeat", "color": "green", "met_value": 8.0, "default_duration": 30, "display_order": 29},
    {"name": "Functional Training", "category": "strength", "icon": "move", "color": "teal", "met_value": 5.0, "default_duration": 30, "display_order": 30},
    {"name": "Pilates", "category": "strength", "icon": "sparkles", "color": "pink", "met_value": 3.0, "default_duration": 45, "display_order": 31},
    {"name": "Core Workout", "category": "strength", "icon": "target", "color": "indigo", "met_value": 5.0, "default_duration": 20, "display_order": 32},

    # Mind & Body (category: mind_body)
    {"name": "Yoga", "category": "mind_body", "icon": "sparkles", "color": "violet", "met_value": 2.5, "default_duration": 45, "display_order": 33},
    {"name": "Meditation", "category": "mind_body", "icon": "brain", "color": "purple", "met_value": 1.5, "default_duration": 20, "display_order": 34},
    {"name": "Stretching", "category": "mind_body", "icon": "move", "color": "teal", "met_value": 2.5, "default_duration": 15, "display_order": 35},
    {"name": "Tai Chi", "category": "mind_body", "icon": "wind", "color": "cyan", "met_value": 3.0, "default_duration": 30, "display_order": 36},
    {"name": "Breathing Exercises", "category": "mind_body", "icon": "wind", "color": "sky", "met_value": 1.5, "default_duration": 10, "display_order": 37},
    {"name": "Foam Rolling", "category": "mind_body", "icon": "circle", "color": "gray", "met_value": 2.0, "default_duration": 15, "display_order": 38},

    # Outdoor & Adventure (category: outdoor)
    {"name": "Hiking", "category": "outdoor", "icon": "mountain", "color": "green", "met_value": 6.0, "default_duration": 60, "display_order": 39},
    {"name": "Rock Climbing", "category": "outdoor", "icon": "mountain", "color": "stone", "met_value": 8.0, "default_duration": 60, "display_order": 40},
    {"name": "Kayaking", "category": "outdoor", "icon": "ship", "color": "blue", "met_value": 5.0, "default_duration": 45, "display_order": 41},
    {"name": "Skiing", "category": "outdoor", "icon": "snowflake", "color": "sky", "met_value": 7.0, "default_duration": 60, "display_order": 42},
    {"name": "Snowboarding", "category": "outdoor", "icon": "snowflake", "color": "cyan", "met_value": 5.5, "default_duration": 60, "display_order": 43},
    {"name": "Surfing", "category": "outdoor", "icon": "waves", "color": "blue", "met_value": 3.0, "default_duration": 60, "display_order": 44},
    {"name": "Skateboarding", "category": "outdoor", "icon": "square", "color": "gray", "met_value": 5.0, "default_duration": 30, "display_order": 45},
    {"name": "Martial Arts", "category": "outdoor", "icon": "swords", "color": "red", "met_value": 10.0, "default_duration": 60, "display_order": 46},

    # Home & Daily (category: home)
    {"name": "Home Workout", "category": "home", "icon": "home", "color": "indigo", "met_value": 5.0, "default_duration": 30, "display_order": 47},
    {"name": "Gardening", "category": "home", "icon": "flower", "color": "green", "met_value": 3.5, "default_duration": 45, "display_order": 48},
    {"name": "Housework", "category": "home", "icon": "home", "color": "amber", "met_value": 3.0, "default_duration": 30, "display_order": 49},
    {"name": "Dog Walking", "category": "home", "icon": "dog", "color": "amber", "met_value": 3.0, "default_duration": 30, "display_order": 50},
    {"name": "Playing with Kids", "category": "home", "icon": "baby", "color": "pink", "met_value": 4.0, "default_duration": 30, "display_order": 51},
    {"name": "Other", "category": "home", "icon": "activity", "color": "gray", "met_value": 4.0, "default_duration": 30, "display_order": 52},
]

def seed_activity_types():
    """Seed activity types if they don't exist."""
    from database import SessionLocal
    db = SessionLocal()
    try:
        # Check if already seeded
        existing_count = db.query(ActivityType).count()
        if existing_count > 0:
            return  # Already seeded

        for activity_data in ACTIVITY_TYPES_SEED:
            activity = ActivityType(**activity_data)
            db.add(activity)

        db.commit()
        print(f"Seeded {len(ACTIVITY_TYPES_SEED)} activity types")
    except Exception as e:
        db.rollback()
        print(f"Error seeding activity types: {e}")
    finally:
        db.close()

# Run seeding on startup
seed_activity_types()

app = FastAPI(title="Daily Tracker API")

# CORS for frontend
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174")
ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()]

is_production = os.getenv("RENDER", "").lower() == "true"

# Always include GitHub Pages origin for hosted SPA
if "https://rakesh-arrepu.github.io" not in ALLOWED_ORIGINS:
    ALLOWED_ORIGINS.append("https://rakesh-arrepu.github.io")

# Choose secure cookie defaults based on environment, then allow env overrides.
# In production we must use SameSite=None and Secure=true for cross-site (github.io → onrender.com).
_default_samesite = "none" if is_production else "lax"
_default_secure = "true" if is_production else "false"

_cookie_samesite_raw = os.getenv("COOKIE_SAMESITE", _default_samesite).lower()
COOKIE_SAMESITE: Literal['lax','strict','none'] = cast(Literal['lax','strict','none'], _default_samesite)
if _cookie_samesite_raw in ('lax','strict','none'):
    COOKIE_SAMESITE = cast(Literal['lax','strict','none'], _cookie_samesite_raw)

COOKIE_SECURE = os.getenv("COOKIE_SECURE", _default_secure).lower() == "true"

# Force cross-site cookie attributes when frontend is hosted on a different origin (e.g., GitHub Pages)
# This ensures browser will send cookies on XHR/fetch with credentials across origins.
if any(("github.io" in o) for o in ALLOWED_ORIGINS):
    COOKIE_SAMESITE = cast(Literal['lax','strict','none'], 'none')
    COOKIE_SECURE = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== Pydantic Schemas ==============

# Password validation constants
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 128
MAX_NAME_LENGTH = 100
MAX_GROUP_NAME_LENGTH = 100
MAX_ENTRY_CONTENT_LENGTH = 5000
VALID_SECTIONS = {"health", "happiness", "hela"}


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(f'Password must be at least {MIN_PASSWORD_LENGTH} characters')
        if len(v) > MAX_PASSWORD_LENGTH:
            raise ValueError(f'Password must be less than {MAX_PASSWORD_LENGTH} characters')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Name is required')
        if len(v) > MAX_NAME_LENGTH:
            raise ValueError(f'Name must be less than {MAX_NAME_LENGTH} characters')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v:
            raise ValueError('Password is required')
        return v


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str

    @field_validator('token')
    @classmethod
    def validate_token(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Reset token is required')
        return v.strip()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(f'Password must be at least {MIN_PASSWORD_LENGTH} characters')
        if len(v) > MAX_PASSWORD_LENGTH:
            raise ValueError(f'Password must be less than {MAX_PASSWORD_LENGTH} characters')
        return v


class UserResponse(BaseModel):
    id: int
    email: str
    name: str


class AuthResponse(BaseModel):
    """Response for login/register with token for cross-origin auth"""
    id: int
    email: str
    name: str
    token: str  # JWT token for Authorization header


class GroupCreate(BaseModel):
    name: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Group name is required')
        if len(v) > MAX_GROUP_NAME_LENGTH:
            raise ValueError(f'Group name must be less than {MAX_GROUP_NAME_LENGTH} characters')
        return v


class GroupResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    is_owner: bool = False


class GroupUpdate(BaseModel):
    name: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Group name is required')
        if len(v) > MAX_GROUP_NAME_LENGTH:
            raise ValueError(f'Group name must be less than {MAX_GROUP_NAME_LENGTH} characters')
        return v


class MemberAdd(BaseModel):
    email: EmailStr


class MemberResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: str


class TransferOwnershipRequest(BaseModel):
    new_owner_id: int


class EntryCreate(BaseModel):
    group_id: int
    section: str  # 'health', 'happiness', 'hela'
    content: str
    entry_date: Optional[date] = None

    @field_validator('section')
    @classmethod
    def validate_section(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in VALID_SECTIONS:
            raise ValueError(f'Section must be one of: {", ".join(VALID_SECTIONS)}')
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Entry content is required')
        if len(v) > MAX_ENTRY_CONTENT_LENGTH:
            raise ValueError(f'Entry content must be less than {MAX_ENTRY_CONTENT_LENGTH} characters')
        return v


class EntryResponse(BaseModel):
    id: int
    section: str
    content: str
    date: date
    user_id: int
    user_name: str


class StreakResponse(BaseModel):
    streak: int
    last_complete_date: Optional[date] = None


class HistoryDay(BaseModel):
    date: date
    completed_sections: list[str]
    is_complete: bool


# ============== Health Activity Schemas ==============

class ActivityTypeResponse(BaseModel):
    id: int
    name: str
    category: str
    icon: str
    color: str
    met_value: float
    default_duration: int


class ActivityTypeGrouped(BaseModel):
    category: str
    activities: list[ActivityTypeResponse]


class HealthActivityCreate(BaseModel):
    group_id: int
    activity_type_id: int
    entry_date: Optional[date] = None
    duration: Optional[int] = None
    duration_unit: str = "minutes"
    distance: Optional[float] = None
    notes: Optional[str] = None

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError('Duration must be positive')
        if v is not None and v > 1440:  # Max 24 hours in minutes
            raise ValueError('Duration cannot exceed 24 hours')
        return v

    @field_validator('duration_unit')
    @classmethod
    def validate_duration_unit(cls, v: str) -> str:
        if v not in ('minutes', 'hours'):
            raise ValueError('Duration unit must be "minutes" or "hours"')
        return v

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) > 500:
                raise ValueError('Notes must be less than 500 characters')
        return v if v else None


class HealthActivityUpdate(BaseModel):
    duration: Optional[int] = None
    duration_unit: Optional[str] = None
    distance: Optional[float] = None
    notes: Optional[str] = None

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError('Duration must be positive')
        if v is not None and v > 1440:
            raise ValueError('Duration cannot exceed 24 hours')
        return v

    @field_validator('duration_unit')
    @classmethod
    def validate_duration_unit(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ('minutes', 'hours'):
            raise ValueError('Duration unit must be "minutes" or "hours"')
        return v


class HealthActivityResponse(BaseModel):
    id: int
    activity_type: ActivityTypeResponse
    duration: Optional[int]
    duration_unit: str
    distance: Optional[float]
    calories: int
    notes: Optional[str]
    created_at: datetime


class DailyHealthSummary(BaseModel):
    date: date
    activities: list[HealthActivityResponse]
    summary: dict  # total_duration_minutes, total_calories, activity_count
    legacy_content: Optional[str] = None  # For backward compatibility with old text entries


class QuickLogRequest(BaseModel):
    group_id: int
    activity_type_id: int
    entry_date: Optional[date] = None


class FavoriteCreate(BaseModel):
    activity_type_id: int


class FavoriteResponse(BaseModel):
    id: int
    activity_type: ActivityTypeResponse
    display_order: int


class HealthAnalyticsResponse(BaseModel):
    period: str
    summary: dict
    activity_breakdown: list[dict]
    daily_trend: list[dict]
    category_breakdown: list[dict]


# ============== Auth Dependency ==============

def get_current_user(
    authorization: str | None = Header(default=None),
    session: str | None = Cookie(default=None),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from Authorization header (Bearer token) or session cookie.
    Priority: Authorization header > Cookie (for cross-origin support)
    """
    token = None

    # Check Authorization header first (for cross-origin requests)
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    # Fall back to cookie (for same-origin/local dev)
    elif session:
        token = session

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = verify_session_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# ============== Auth Endpoints ==============

@app.post("/api/auth/register", response_model=AuthResponse)
def register(user_data: UserCreate, response: Response, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Returns:
        AuthResponse with the created user's info and authentication token

    Errors:
        400: Email already registered, or validation error
        500: Database error
    """
    try:
        # Check if email exists
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user
        user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            name=user_data.name.strip()
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Send welcome email (non-blocking)
        if is_email_configured():
            success, error = send_welcome_email(user.email, user.name)
            if not success:
                logger.warning(f"Failed to send welcome email to {user.email}: {error}")

        # Create session token
        token = create_session_token(cast(int, user.id))

        # Set cookie for local dev (optional, won't work cross-origin)
        set_session_cookie(response, token)

        # Return token in response body for cross-origin auth
        return AuthResponse(
            id=cast(int, user.id),
            email=cast(str, user.email),
            name=cast(str, user.name),
            token=token
        )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create account. Please try again.")


@app.post("/api/auth/login", response_model=AuthResponse)
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
    Authenticate user and create session.

    Returns:
        AuthResponse with the user's info and authentication token

    Errors:
        401: Invalid email or password
        500: Database error
    """
    try:
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user or not verify_password(user_data.password, cast(str, user.password_hash)):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Create session token
        token = create_session_token(cast(int, user.id))

        # Set cookie for local dev (optional, won't work cross-origin)
        set_session_cookie(response, token)

        # Return token in response body for cross-origin auth
        return AuthResponse(
            id=cast(int, user.id),
            email=cast(str, user.email),
            name=cast(str, user.name),
            token=token
        )
    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Login failed. Please try again.")


@app.post("/api/auth/logout")
def logout(response: Response):
    """
    Log out the current user by clearing the session cookie.

    Returns:
        Success message
    """
    response.delete_cookie(key="session", samesite=COOKIE_SAMESITE, secure=COOKIE_SECURE)
    return {"message": "Logged out successfully"}


@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's info.

    Returns:
        UserResponse with the user's info

    Errors:
        401: Not authenticated or session expired
    """
    return UserResponse(id=cast(int, current_user.id), email=cast(str, current_user.email), name=cast(str, current_user.name))


# ============== Password Reset Endpoints ==============

@app.post("/api/auth/password/forgot")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request a password reset token for a given email.
    Sends a password reset email if the account exists.
    Always returns a generic success message for security.

    Returns:
        Success message (and token in development mode if email is not configured)
    """
    generic_message = "If an account exists with this email, a reset link has been sent."

    try:
        user = db.query(User).filter(User.email == payload.email).first()
        if not user:
            # Do not reveal whether the email exists
            return {"message": generic_message}

        token = create_password_reset_token(payload.email)
        response_data = {"message": generic_message}

        # Try to send email
        if is_email_configured():
            success, error = send_password_reset_email(payload.email, token)
            if success:
                response_data["email_sent"] = True
            else:
                # Log the error but don't expose it to user
                # In dev mode, fall back to showing token
                if not is_production:
                    response_data["reset_token"] = token
                    response_data["email_error"] = error
        else:
            # Email not configured - only return token in development mode
            if not is_production:
                response_data["reset_token"] = token
                response_data["email_configured"] = False

        return response_data
    except SQLAlchemyError:
        # Still return success to not reveal information
        return {"message": generic_message}


@app.post("/api/auth/password/reset")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password using a valid reset token.

    Returns:
        Success message

    Errors:
        400: Invalid or expired token
        404: User not found (shouldn't happen normally)
        500: Database error
    """
    try:
        email = verify_password_reset_token(payload.token)
        if not email:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token. Please request a new password reset.")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User account not found")

        user.password_hash = hash_password(payload.password)  # type: ignore[assignment]
        db.add(user)
        db.commit()

        return {"message": "Password has been reset successfully. You can now log in with your new password."}
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to reset password. Please try again.")

# ============== Group Endpoints ==============

@app.get("/api/groups", response_model=list[GroupResponse])
def list_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    List all groups the current user is a member of or owns.

    Returns:
        List of GroupResponse objects

    Errors:
        401: Not authenticated
        500: Database error
    """
    try:
        # Get groups where user is owner or member
        owned = db.query(Group).filter(Group.owner_id == current_user.id).all()
        member_of = db.query(Group).join(GroupMember).filter(GroupMember.user_id == current_user.id).all()

        all_groups = {g.id: g for g in owned + member_of}

        return [
            GroupResponse(
                id=cast(int, g.id),
                name=cast(str, g.name),
                owner_id=cast(int, g.owner_id),
                is_owner=g.owner_id == current_user.id
            )
            for g in all_groups.values()
        ]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Failed to load groups. Please try again.")


@app.post("/api/groups", response_model=GroupResponse)
def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new group with the current user as owner.

    Returns:
        GroupResponse with the created group

    Errors:
        400: Validation error (empty name, etc.)
        401: Not authenticated
        500: Database error
    """
    try:
        group = Group(name=group_data.name.strip(), owner_id=current_user.id)
        db.add(group)
        db.commit()
        db.refresh(group)

        # Add owner as member too
        member = GroupMember(group_id=group.id, user_id=current_user.id)
        db.add(member)
        db.commit()

        return GroupResponse(id=cast(int, group.id), name=cast(str, group.name), owner_id=cast(int, group.owner_id), is_owner=True)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create group. Please try again.")


@app.put("/api/groups/{group_id}", response_model=GroupResponse)
def update_group(
    group_id: int,
    group_data: GroupUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a group's name. Only the owner can update.

    Returns:
        GroupResponse with the updated group

    Errors:
        400: Validation error (empty name, etc.)
        401: Not authenticated
        403: Only owner can update group
        404: Group not found
        500: Database error
    """
    try:
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Only owner can update group
        if group.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only the group owner can update the group")

        # Update group name
        group.name = group_data.name.strip()  # type: ignore[assignment]
        db.commit()
        db.refresh(group)

        return GroupResponse(id=cast(int, group.id), name=cast(str, group.name), owner_id=cast(int, group.owner_id), is_owner=True)
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update group. Please try again.")


@app.get("/api/groups/{group_id}/members", response_model=list[MemberResponse])
def list_members(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all members of a group.

    Returns:
        List of MemberResponse objects

    Errors:
        401: Not authenticated
        403: Not a member of the group
        404: Group not found
        500: Database error
    """
    try:
        # Verify user has access to group
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        is_member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id
        ).first()

        if not is_member and group.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not a member of this group")

        members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()

        return [
            MemberResponse(
                id=cast(int, m.id),
                user_id=cast(int, m.user.id),
                name=cast(str, m.user.name),
                email=cast(str, m.user.email)
            )
            for m in members
        ]
    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Failed to load members. Please try again.")


@app.post("/api/groups/{group_id}/members", response_model=MemberResponse)
def add_member(
    group_id: int,
    member_data: MemberAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new member to a group by email.

    Returns:
        MemberResponse with the added member

    Errors:
        400: User already a member
        401: Not authenticated
        403: Only owner can add members
        404: Group or user not found
        500: Database error
    """
    try:
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        if group.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only the group owner can add members")

        user = db.query(User).filter(User.email == member_data.email).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"No user found with email '{member_data.email}'")

        existing = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="User is already a member of this group")

        member = GroupMember(group_id=group_id, user_id=user.id)
        db.add(member)
        db.commit()
        db.refresh(member)

        # Send emails to both member and owner (non-blocking)
        if is_email_configured():
            # Email to new member
            success, error = send_member_added_email_to_member(
                user.email, user.name, group.name, group_id, current_user.name
            )
            if not success:
                logger.warning(f"Failed to send member-added email to {user.email}: {error}")

            # Email to owner
            success, error = send_member_added_email_to_owner(
                current_user.email, current_user.name, user.name, user.email, group.name, group_id
            )
            if not success:
                logger.warning(f"Failed to send member-added email to owner {current_user.email}: {error}")

        return MemberResponse(id=cast(int, member.id), user_id=cast(int, user.id), name=cast(str, user.name), email=cast(str, user.email))
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add member. Please try again.")


@app.delete("/api/groups/{group_id}/members/{user_id}")
def remove_member(
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a member from a group.

    Returns:
        Success message

    Errors:
        400: Cannot remove owner from group
        401: Not authenticated
        403: Only owner can remove members
        404: Group or member not found
        500: Database error
    """
    try:
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        if group.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only the group owner can remove members")

        if user_id == group.owner_id:
            raise HTTPException(status_code=400, detail="Cannot remove the group owner from the group")

        member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        ).first()

        if not member:
            raise HTTPException(status_code=404, detail="Member not found in this group")

        db.delete(member)
        db.commit()

        return {"message": "Member removed successfully"}
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to remove member. Please try again.")

@app.put("/api/groups/{group_id}/owner")
def transfer_ownership(
    group_id: int,
    request: TransferOwnershipRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Transfer group ownership to another member.

    Args:
        group_id: The group to transfer
        new_owner_id: The user ID of the new owner (must be a member)

    Returns:
        Success message with updated group info

    Errors:
        400: New owner is not a member or is already the owner
        401: Not authenticated
        403: Only current owner can transfer ownership
        404: Group not found
        500: Database error
    """
    try:
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Only current owner can transfer
        if group.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only the current owner can transfer ownership")

        # Cannot transfer to yourself
        if request.new_owner_id == current_user.id:
            raise HTTPException(status_code=400, detail="You are already the owner of this group")

        # Verify new owner is a member
        is_member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == request.new_owner_id
        ).first()

        if not is_member:
            raise HTTPException(status_code=400, detail="New owner must be a member of the group")

        # Get new owner user info for response
        new_owner = db.query(User).filter(User.id == request.new_owner_id).first()
        if not new_owner:
            raise HTTPException(status_code=404, detail="New owner user not found")

        # Transfer ownership
        group.owner_id = request.new_owner_id  # type: ignore[assignment]
        db.commit()
        db.refresh(group)

        # Send emails to both new owner and previous owner (non-blocking)
        if is_email_configured():
            # Email to new owner
            success, error = send_ownership_transfer_email_to_new_owner(
                new_owner.email, new_owner.name, group.name, group_id, current_user.name
            )
            if not success:
                logger.warning(f"Failed to send ownership transfer email to new owner {new_owner.email}: {error}")

            # Email to previous owner
            success, error = send_ownership_transfer_email_to_previous_owner(
                current_user.email, current_user.name, group.name, group_id, new_owner.name
            )
            if not success:
                logger.warning(f"Failed to send ownership transfer email to previous owner {current_user.email}: {error}")

        return {
            "message": f"Ownership transferred successfully to {new_owner.name}",
            "group": GroupResponse(
                id=cast(int, group.id),
                name=cast(str, group.name),
                owner_id=cast(int, group.owner_id),
                is_owner=False  # Current user is no longer owner
            )
        }
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to transfer ownership. Please try again.")


# ============== Entry Endpoints ==============

@app.get("/api/entries", response_model=list[EntryResponse])
def get_entries(
    group_id: int,
    entry_date: Optional[date] = None,
    user_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get entries for a group, optionally filtered by date and user.

    Args:
        group_id: The group to get entries for
        entry_date: Optional date filter (YYYY-MM-DD format)
        user_id: Optional user ID filter (owner-only, defaults to current user)

    Returns:
        List of EntryResponse objects

    Errors:
        400: Invalid date or parameters
        401: Not authenticated
        403: Not a member of this group, or non-owner trying to view other users' data
        404: Group not found, or requested user not a member
        500: Database error
    """
    try:
        # Verify group exists
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Verify membership
        is_member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id
        ).first()

        if not is_member:
            raise HTTPException(status_code=403, detail="You are not a member of this group")

        # Determine which user's entries to fetch
        target_user_id = current_user.id  # Default: current user only (SECURITY FIX)

        if user_id is not None:
            # Someone is requesting another user's data
            if not verify_group_owner(db, group_id, current_user.id):
                raise HTTPException(status_code=403, detail="Only group owners can view other members' data")

            # Verify requested user is a member
            is_target_member = db.query(GroupMember).filter(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            ).first()

            if not is_target_member:
                raise HTTPException(status_code=404, detail="User is not a member of this group")

            target_user_id = user_id

        # CRITICAL FIX: Add user filter (was missing!)
        query = db.query(Entry).filter(
            Entry.group_id == group_id,
            Entry.user_id == target_user_id
        )

        if entry_date:
            # Validate date is not in the future
            if entry_date > date.today():
                raise HTTPException(status_code=400, detail="Cannot query entries for future dates")
            query = query.filter(Entry.date == entry_date)

        entries = query.all()

        return [
            EntryResponse(
                id=cast(int, e.id),
                section=cast(str, e.section),
                content=cast(str, e.content),
                date=e.date,
                user_id=cast(int, e.user_id),
                user_name=cast(str, e.user.name)
            )
            for e in entries
        ]
    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Failed to load entries. Please try again.")


@app.post("/api/entries", response_model=EntryResponse)
def create_or_update_entry(
    entry_data: EntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or update an entry for a specific date and section.
    If an entry already exists for the same user, group, section, and date, it will be updated.

    Returns:
        EntryResponse with the created/updated entry

    Errors:
        400: Validation error (invalid section, future date, empty content)
        401: Not authenticated
        403: Not a member of this group
        404: Group not found
        500: Database error
    """
    try:
        # Verify group exists
        group = db.query(Group).filter(Group.id == entry_data.group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Verify membership
        is_member = db.query(GroupMember).filter(
            GroupMember.group_id == entry_data.group_id,
            GroupMember.user_id == current_user.id
        ).first()

        if not is_member:
            raise HTTPException(status_code=403, detail="You are not a member of this group")

        entry_date = entry_data.entry_date or date.today()

        # Validate date is not in the future
        if entry_date > date.today():
            raise HTTPException(status_code=400, detail="Cannot create entries for future dates")

        # Check for existing entry
        existing = db.query(Entry).filter(
            Entry.user_id == current_user.id,
            Entry.group_id == entry_data.group_id,
            Entry.section == entry_data.section,
            Entry.date == entry_date
        ).first()

        if existing:
            # Update existing
            existing.content = entry_data.content  # type: ignore[assignment]
            existing.updated_at = datetime.utcnow()  # type: ignore[assignment]
            db.commit()
            db.refresh(existing)
            entry = existing
        else:
            # Create new
            entry = Entry(
                user_id=current_user.id,
                group_id=entry_data.group_id,
                section=entry_data.section,
                content=entry_data.content,
                date=entry_date
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)

        return EntryResponse(
            id=cast(int, entry.id),
            section=cast(str, entry.section),
            content=cast(str, entry.content),
            date=entry.date,
            user_id=cast(int, entry.user_id),
            user_name=cast(str, current_user.name)
        )
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save entry. Please try again.")

# ============== Analytics Endpoints ==============

# Constants for analytics validation
MAX_HISTORY_DAYS = 365
DEFAULT_HISTORY_DAYS = 30


@app.get("/api/analytics/streak", response_model=StreakResponse)
def get_streak(
    group_id: int,
    user_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current streak (consecutive days with all 3 sections completed) for a user in a group.

    Args:
        group_id: The group to get streak for
        user_id: Optional user ID filter (owner-only, defaults to current user)

    Returns:
        StreakResponse with streak count and last complete date

    Errors:
        401: Not authenticated
        403: Not a member of this group, or non-owner trying to view other users' data
        404: Group not found, or requested user not a member
        500: Database error
    """
    try:
        # Verify group exists
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Verify membership
        is_member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id
        ).first()

        if not is_member:
            raise HTTPException(status_code=403, detail="You are not a member of this group")

        # Determine which user's streak to fetch
        target_user_id = current_user.id  # Default: current user only

        if user_id is not None:
            # Someone is requesting another user's data
            if not verify_group_owner(db, group_id, current_user.id):
                raise HTTPException(status_code=403, detail="Only group owners can view other members' data")

            # Verify requested user is a member
            is_target_member = db.query(GroupMember).filter(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            ).first()

            if not is_target_member:
                raise HTTPException(status_code=404, detail="User is not a member of this group")

            target_user_id = user_id

        # Get all complete days (3 sections) for this user in this group
        complete_days = (
            db.query(Entry.date)
            .filter(
                Entry.user_id == target_user_id,
                Entry.group_id == group_id
            )
            .group_by(Entry.date)
            .having(func.count(func.distinct(Entry.section)) == 3)
            .order_by(Entry.date.desc())
            .all()
        )

        if not complete_days:
            return StreakResponse(streak=0)

        complete_dates = sorted([d[0] for d in complete_days], reverse=True)

        # Calculate streak from today backwards
        streak = 0
        check_date = date.today()

        for d in complete_dates:
            if d == check_date:
                streak += 1
                check_date -= timedelta(days=1)
            elif d == check_date - timedelta(days=1):
                # Allow for checking yesterday if today not complete yet
                check_date = d
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        last_complete = complete_dates[0] if complete_dates else None

        return StreakResponse(streak=streak, last_complete_date=last_complete)
    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Failed to calculate streak. Please try again.")


@app.get("/api/analytics/history", response_model=list[HistoryDay])
def get_history(
    group_id: int,
    days: int = DEFAULT_HISTORY_DAYS,
    user_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the history of completed sections for a user in a group.

    Args:
        group_id: The group to get history for
        days: Number of days to look back (default 30, max 365)
        user_id: Optional user ID filter (owner-only, defaults to current user)

    Returns:
        List of HistoryDay objects sorted by date descending

    Errors:
        400: Invalid days parameter
        401: Not authenticated
        403: Not a member of this group, or non-owner trying to view other users' data
        404: Group not found, or requested user not a member
        500: Database error
    """
    try:
        # Validate days parameter
        if days < 1:
            raise HTTPException(status_code=400, detail="Days parameter must be at least 1")
        if days > MAX_HISTORY_DAYS:
            raise HTTPException(status_code=400, detail=f"Days parameter cannot exceed {MAX_HISTORY_DAYS}")

        # Verify group exists
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Verify membership
        is_member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id
        ).first()

        if not is_member:
            raise HTTPException(status_code=403, detail="You are not a member of this group")

        # Determine which user's history to fetch
        target_user_id = current_user.id  # Default: current user only

        if user_id is not None:
            # Someone is requesting another user's data
            if not verify_group_owner(db, group_id, current_user.id):
                raise HTTPException(status_code=403, detail="Only group owners can view other members' data")

            # Verify requested user is a member
            is_target_member = db.query(GroupMember).filter(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            ).first()

            if not is_target_member:
                raise HTTPException(status_code=404, detail="User is not a member of this group")

            target_user_id = user_id

        start_date = date.today() - timedelta(days=days)

        entries = db.query(Entry).filter(
            Entry.user_id == target_user_id,
            Entry.group_id == group_id,
            Entry.date >= start_date
        ).all()

        # Group by date
        by_date: dict[date, list[str]] = {}
        for e in entries:
            if e.date not in by_date:
                by_date[e.date] = []
            by_date[e.date].append(cast(str, e.section))

        # Build response for all days
        result = []
        for i in range(days + 1):
            d = date.today() - timedelta(days=i)
            sections = by_date.get(d, [])
            result.append(HistoryDay(
                date=d,
                completed_sections=sections,
                is_complete=len(set(sections)) == 3
            ))

        return sorted(result, key=lambda x: x.date, reverse=True)
    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Failed to load history. Please try again.")


# ============== Health Activity Endpoints ==============

# Calorie calculation helper
DEFAULT_WEIGHT_KG = 70  # Default weight for calorie calculation

def calculate_calories(met_value: float, duration_minutes: int) -> int:
    """
    Calculate calories burned using MET formula.
    Calories = MET * weight(kg) * duration(hours)
    """
    duration_hours = duration_minutes / 60
    return round(met_value * DEFAULT_WEIGHT_KG * duration_hours)


def build_activity_type_response(activity_type: ActivityType) -> ActivityTypeResponse:
    """Build ActivityTypeResponse from ActivityType model."""
    return ActivityTypeResponse(
        id=cast(int, activity_type.id),
        name=cast(str, activity_type.name),
        category=cast(str, activity_type.category),
        icon=cast(str, activity_type.icon),
        color=cast(str, activity_type.color),
        met_value=cast(float, activity_type.met_value),
        default_duration=cast(int, activity_type.default_duration)
    )


def build_health_activity_response(activity: HealthActivity) -> HealthActivityResponse:
    """Build HealthActivityResponse from HealthActivity model."""
    return HealthActivityResponse(
        id=cast(int, activity.id),
        activity_type=build_activity_type_response(activity.activity_type),
        duration=activity.duration,
        duration_unit=cast(str, activity.duration_unit),
        distance=activity.distance,
        calories=cast(int, activity.calories),
        notes=activity.notes,
        created_at=activity.created_at
    )


@app.get("/api/activity-types", response_model=list[ActivityTypeGrouped])
def get_activity_types(db: Session = Depends(get_db)):
    """
    Get all active activity types grouped by category.

    Returns:
        List of ActivityTypeGrouped objects with activities organized by category

    Errors:
        500: Database error
    """
    try:
        activities = db.query(ActivityType).filter(
            ActivityType.is_active == True
        ).order_by(ActivityType.display_order).all()

        # Group by category
        categories: dict[str, list[ActivityTypeResponse]] = {}
        category_order = ["cardio", "sports", "strength", "mind_body", "outdoor", "home"]

        for activity in activities:
            category = cast(str, activity.category)
            if category not in categories:
                categories[category] = []
            categories[category].append(build_activity_type_response(activity))

        # Return in defined order
        result = []
        for cat in category_order:
            if cat in categories:
                result.append(ActivityTypeGrouped(category=cat, activities=categories[cat]))

        return result
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Failed to load activity types. Please try again.")


@app.get("/api/health-activities", response_model=DailyHealthSummary)
def get_health_activities(
    group_id: int,
    entry_date: Optional[date] = None,
    user_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get health activities for a specific date.

    Args:
        group_id: The group to get activities for
        entry_date: Date to get activities for (defaults to today)
        user_id: Optional user ID filter (owner-only)

    Returns:
        DailyHealthSummary with activities and summary stats

    Errors:
        401: Not authenticated
        403: Not a member of this group, or non-owner trying to view other users' data
        404: Group not found
        500: Database error
    """
    try:
        # Verify group exists
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Verify membership
        is_member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id
        ).first()

        if not is_member:
            raise HTTPException(status_code=403, detail="You are not a member of this group")

        # Determine which user's data to fetch
        target_user_id = current_user.id

        if user_id is not None:
            if not verify_group_owner(db, group_id, current_user.id):
                raise HTTPException(status_code=403, detail="Only group owners can view other members' data")
            target_user_id = user_id

        target_date = entry_date or date.today()

        # Get health activities
        activities = db.query(HealthActivity).filter(
            HealthActivity.user_id == target_user_id,
            HealthActivity.group_id == group_id,
            HealthActivity.date == target_date
        ).order_by(HealthActivity.created_at).all()

        # Calculate summary
        total_duration = 0
        total_calories = 0
        for a in activities:
            if a.duration:
                duration_mins = a.duration if a.duration_unit == "minutes" else a.duration * 60
                total_duration += duration_mins
            total_calories += cast(int, a.calories)

        # Check for legacy text entry
        legacy_entry = db.query(Entry).filter(
            Entry.user_id == target_user_id,
            Entry.group_id == group_id,
            Entry.section == "health",
            Entry.date == target_date
        ).first()

        legacy_content = cast(str, legacy_entry.content) if legacy_entry else None

        return DailyHealthSummary(
            date=target_date,
            activities=[build_health_activity_response(a) for a in activities],
            summary={
                "total_duration_minutes": total_duration,
                "total_calories": total_calories,
                "activity_count": len(activities)
            },
            legacy_content=legacy_content
        )
    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Failed to load health activities. Please try again.")


@app.post("/api/health-activities", response_model=HealthActivityResponse)
def create_health_activity(
    data: HealthActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log a new health activity.

    Returns:
        HealthActivityResponse with the created activity

    Errors:
        400: Validation error, future date
        401: Not authenticated
        403: Not a member of this group
        404: Group or activity type not found
        500: Database error
    """
    try:
        # Verify group exists
        group = db.query(Group).filter(Group.id == data.group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Verify membership
        is_member = db.query(GroupMember).filter(
            GroupMember.group_id == data.group_id,
            GroupMember.user_id == current_user.id
        ).first()

        if not is_member:
            raise HTTPException(status_code=403, detail="You are not a member of this group")

        # Verify activity type exists
        activity_type = db.query(ActivityType).filter(
            ActivityType.id == data.activity_type_id,
            ActivityType.is_active == True
        ).first()

        if not activity_type:
            raise HTTPException(status_code=404, detail="Activity type not found")

        entry_date = data.entry_date or date.today()

        # Validate date is not in the future
        if entry_date > date.today():
            raise HTTPException(status_code=400, detail="Cannot log activities for future dates")

        # Calculate calories
        duration_mins = data.duration or cast(int, activity_type.default_duration)
        if data.duration_unit == "hours":
            duration_mins = duration_mins * 60

        calories = calculate_calories(cast(float, activity_type.met_value), duration_mins)

        # Create activity
        activity = HealthActivity(
            user_id=current_user.id,
            group_id=data.group_id,
            activity_type_id=data.activity_type_id,
            date=entry_date,
            duration=data.duration,
            duration_unit=data.duration_unit,
            distance=data.distance,
            calories=calories,
            notes=data.notes
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)

        return build_health_activity_response(activity)
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to log activity. Please try again.")


@app.put("/api/health-activities/{activity_id}", response_model=HealthActivityResponse)
def update_health_activity(
    activity_id: int,
    data: HealthActivityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing health activity.

    Returns:
        HealthActivityResponse with the updated activity

    Errors:
        401: Not authenticated
        403: Cannot update another user's activity
        404: Activity not found
        500: Database error
    """
    try:
        activity = db.query(HealthActivity).filter(HealthActivity.id == activity_id).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        if activity.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot update another user's activity")

        # Update fields if provided
        if data.duration is not None:
            activity.duration = data.duration  # type: ignore[assignment]
        if data.duration_unit is not None:
            activity.duration_unit = data.duration_unit  # type: ignore[assignment]
        if data.distance is not None:
            activity.distance = data.distance  # type: ignore[assignment]
        if data.notes is not None:
            activity.notes = data.notes  # type: ignore[assignment]

        # Recalculate calories
        duration_mins = activity.duration or cast(int, activity.activity_type.default_duration)
        if activity.duration_unit == "hours":
            duration_mins = duration_mins * 60

        activity.calories = calculate_calories(cast(float, activity.activity_type.met_value), duration_mins)  # type: ignore[assignment]
        activity.updated_at = datetime.utcnow()  # type: ignore[assignment]

        db.commit()
        db.refresh(activity)

        return build_health_activity_response(activity)
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update activity. Please try again.")


@app.delete("/api/health-activities/{activity_id}")
def delete_health_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a health activity.

    Returns:
        Success message

    Errors:
        401: Not authenticated
        403: Cannot delete another user's activity
        404: Activity not found
        500: Database error
    """
    try:
        activity = db.query(HealthActivity).filter(HealthActivity.id == activity_id).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        if activity.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot delete another user's activity")

        db.delete(activity)
        db.commit()

        return {"message": "Activity deleted successfully"}
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete activity. Please try again.")


@app.post("/api/health-activities/quick-log", response_model=HealthActivityResponse)
def quick_log_activity(
    data: QuickLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quick log an activity with default duration.

    Returns:
        HealthActivityResponse with the created activity

    Errors:
        401: Not authenticated
        403: Not a member of this group
        404: Group or activity type not found
        500: Database error
    """
    try:
        # Verify group exists
        group = db.query(Group).filter(Group.id == data.group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Verify membership
        is_member = db.query(GroupMember).filter(
            GroupMember.group_id == data.group_id,
            GroupMember.user_id == current_user.id
        ).first()

        if not is_member:
            raise HTTPException(status_code=403, detail="You are not a member of this group")

        # Verify activity type exists
        activity_type = db.query(ActivityType).filter(
            ActivityType.id == data.activity_type_id,
            ActivityType.is_active == True
        ).first()

        if not activity_type:
            raise HTTPException(status_code=404, detail="Activity type not found")

        entry_date = data.entry_date or date.today()

        # Validate date is not in the future
        if entry_date > date.today():
            raise HTTPException(status_code=400, detail="Cannot log activities for future dates")

        # Use default duration
        default_duration = cast(int, activity_type.default_duration)
        calories = calculate_calories(cast(float, activity_type.met_value), default_duration)

        # Create activity
        activity = HealthActivity(
            user_id=current_user.id,
            group_id=data.group_id,
            activity_type_id=data.activity_type_id,
            date=entry_date,
            duration=default_duration,
            duration_unit="minutes",
            calories=calories
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)

        return build_health_activity_response(activity)
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to log activity. Please try again.")


# ============== Favorites Endpoints ==============

@app.get("/api/health-activities/favorites", response_model=list[FavoriteResponse])
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's favorite activities for quick-log.

    Returns:
        List of FavoriteResponse objects sorted by display_order

    Errors:
        401: Not authenticated
        500: Database error
    """
    try:
        favorites = db.query(UserActivityFavorite).filter(
            UserActivityFavorite.user_id == current_user.id
        ).order_by(UserActivityFavorite.display_order).all()

        return [
            FavoriteResponse(
                id=cast(int, f.id),
                activity_type=build_activity_type_response(f.activity_type),
                display_order=cast(int, f.display_order)
            )
            for f in favorites
        ]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Failed to load favorites. Please try again.")


@app.post("/api/health-activities/favorites", response_model=FavoriteResponse)
def add_favorite(
    data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add an activity to favorites.

    Returns:
        FavoriteResponse with the created favorite

    Errors:
        400: Already a favorite
        401: Not authenticated
        404: Activity type not found
        500: Database error
    """
    try:
        # Verify activity type exists
        activity_type = db.query(ActivityType).filter(
            ActivityType.id == data.activity_type_id,
            ActivityType.is_active == True
        ).first()

        if not activity_type:
            raise HTTPException(status_code=404, detail="Activity type not found")

        # Check if already favorited
        existing = db.query(UserActivityFavorite).filter(
            UserActivityFavorite.user_id == current_user.id,
            UserActivityFavorite.activity_type_id == data.activity_type_id
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Activity already in favorites")

        # Get next display order
        max_order = db.query(func.max(UserActivityFavorite.display_order)).filter(
            UserActivityFavorite.user_id == current_user.id
        ).scalar() or 0

        favorite = UserActivityFavorite(
            user_id=current_user.id,
            activity_type_id=data.activity_type_id,
            display_order=max_order + 1
        )
        db.add(favorite)
        db.commit()
        db.refresh(favorite)

        return FavoriteResponse(
            id=cast(int, favorite.id),
            activity_type=build_activity_type_response(activity_type),
            display_order=cast(int, favorite.display_order)
        )
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add favorite. Please try again.")


@app.delete("/api/health-activities/favorites/{activity_type_id}")
def remove_favorite(
    activity_type_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove an activity from favorites.

    Returns:
        Success message

    Errors:
        401: Not authenticated
        404: Favorite not found
        500: Database error
    """
    try:
        favorite = db.query(UserActivityFavorite).filter(
            UserActivityFavorite.user_id == current_user.id,
            UserActivityFavorite.activity_type_id == activity_type_id
        ).first()

        if not favorite:
            raise HTTPException(status_code=404, detail="Favorite not found")

        db.delete(favorite)
        db.commit()

        return {"message": "Favorite removed successfully"}
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to remove favorite. Please try again.")


# ============== Health Analytics Endpoint ==============

@app.get("/api/analytics/health", response_model=HealthAnalyticsResponse)
def get_health_analytics(
    group_id: int,
    period: str = "month",
    user_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get health analytics for a user in a group.

    Args:
        group_id: The group to get analytics for
        period: Time period - "week", "month", or "year"
        user_id: Optional user ID filter (owner-only)

    Returns:
        HealthAnalyticsResponse with summary, breakdowns, and trends

    Errors:
        400: Invalid period
        401: Not authenticated
        403: Not a member, or non-owner viewing others
        404: Group not found
        500: Database error
    """
    try:
        # Validate period
        if period not in ("week", "month", "year"):
            raise HTTPException(status_code=400, detail="Period must be 'week', 'month', or 'year'")

        # Verify group exists
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Verify membership
        is_member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id
        ).first()

        if not is_member:
            raise HTTPException(status_code=403, detail="You are not a member of this group")

        # Determine which user's data to fetch
        target_user_id = current_user.id

        if user_id is not None:
            if not verify_group_owner(db, group_id, current_user.id):
                raise HTTPException(status_code=403, detail="Only group owners can view other members' data")
            target_user_id = user_id

        # Calculate date range
        today = date.today()
        if period == "week":
            start_date = today - timedelta(days=7)
        elif period == "month":
            start_date = today - timedelta(days=30)
        else:  # year
            start_date = today - timedelta(days=365)

        # Get activities in range
        activities = db.query(HealthActivity).filter(
            HealthActivity.user_id == target_user_id,
            HealthActivity.group_id == group_id,
            HealthActivity.date >= start_date
        ).all()

        # Calculate summary
        total_activities = len(activities)
        total_duration = 0
        total_calories = 0
        active_dates = set()

        for a in activities:
            active_dates.add(a.date)
            total_calories += cast(int, a.calories)
            if a.duration:
                duration_mins = a.duration if a.duration_unit == "minutes" else a.duration * 60
                total_duration += duration_mins

        # Activity breakdown by type
        activity_counts: dict[int, dict] = {}
        for a in activities:
            type_id = cast(int, a.activity_type_id)
            if type_id not in activity_counts:
                activity_counts[type_id] = {
                    "activity_type": build_activity_type_response(a.activity_type).__dict__,
                    "count": 0,
                    "duration": 0,
                    "calories": 0
                }
            activity_counts[type_id]["count"] += 1
            activity_counts[type_id]["calories"] += cast(int, a.calories)
            if a.duration:
                duration_mins = a.duration if a.duration_unit == "minutes" else a.duration * 60
                activity_counts[type_id]["duration"] += duration_mins

        # Calculate percentages
        activity_breakdown = []
        for data in sorted(activity_counts.values(), key=lambda x: x["count"], reverse=True):
            data["percentage"] = round((data["count"] / total_activities * 100) if total_activities > 0 else 0, 1)
            activity_breakdown.append(data)

        # Daily trend
        daily_data: dict[date, dict] = {}
        for a in activities:
            d = a.date
            if d not in daily_data:
                daily_data[d] = {"date": d.isoformat(), "calories": 0, "duration_minutes": 0, "activities": 0}
            daily_data[d]["calories"] += cast(int, a.calories)
            daily_data[d]["activities"] += 1
            if a.duration:
                duration_mins = a.duration if a.duration_unit == "minutes" else a.duration * 60
                daily_data[d]["duration_minutes"] += duration_mins

        daily_trend = sorted(daily_data.values(), key=lambda x: x["date"])

        # Category breakdown
        category_counts: dict[str, dict] = {}
        for a in activities:
            category = cast(str, a.activity_type.category)
            if category not in category_counts:
                category_counts[category] = {"category": category, "count": 0, "calories": 0}
            category_counts[category]["count"] += 1
            category_counts[category]["calories"] += cast(int, a.calories)

        category_breakdown = sorted(category_counts.values(), key=lambda x: x["count"], reverse=True)

        return HealthAnalyticsResponse(
            period=period,
            summary={
                "total_activities": total_activities,
                "total_duration_minutes": total_duration,
                "total_calories": total_calories,
                "active_days": len(active_dates)
            },
            activity_breakdown=activity_breakdown,
            daily_trend=daily_trend,
            category_breakdown=category_breakdown
        )
    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Failed to load health analytics. Please try again.")


# ============== Root ==============
@app.get("/", include_in_schema=False)
def root():
    """Root endpoint with API info."""
    return {"ok": True, "service": "Daily Tracker API", "docs": "/docs", "health": "/api/health"}


# ============== Health Check ==============

@app.get("/api/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "service": "Daily Tracker API"}
