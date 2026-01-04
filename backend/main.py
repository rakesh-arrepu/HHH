from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import Optional, Literal, cast
import os
import re
from fastapi import FastAPI, Depends, HTTPException, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

from database import engine, get_db, Base
from models import User, Group, GroupMember, Entry # type: ignore
from auth import hash_password, verify_password, create_session_token, verify_session_token, create_password_reset_token, verify_password_reset_token
from email_service import send_password_reset_email, is_email_configured


# ============== Error Response Helper ==============

def api_error(status_code: int, detail: str, code: str | None = None) -> HTTPException:
    """Create an HTTPException with optional error code for frontend handling."""
    error_detail = {"detail": detail}
    if code:
        error_detail["code"] = code
    return HTTPException(status_code=status_code, detail=detail)

# Create tables
Base.metadata.create_all(bind=engine)

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


class MemberAdd(BaseModel):
    email: EmailStr


class MemberResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: str


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

# ============== Auth Dependency ==============

def get_current_user(
    session: str = Cookie(default=None),
    db: Session = Depends(get_db)
) -> User:
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = verify_session_token(session)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# ============== Auth Endpoints ==============

@app.post("/api/auth/register", response_model=UserResponse)
def register(user_data: UserCreate, response: Response, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Returns:
        UserResponse with the created user's info

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

        # Set session cookie
        token = create_session_token(cast(int, user.id))
        response.set_cookie(
            key="session",
            value=token,
            httponly=True,
            samesite=COOKIE_SAMESITE,
            secure=COOKIE_SECURE,
            max_age=60 * 60 * 24 * 7  # 7 days
        )

        return UserResponse(id=cast(int, user.id), email=cast(str, user.email), name=cast(str, user.name))
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create account. Please try again.")


@app.post("/api/auth/login", response_model=UserResponse)
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
    Authenticate user and create session.

    Returns:
        UserResponse with the user's info

    Errors:
        401: Invalid email or password
        500: Database error
    """
    try:
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user or not verify_password(user_data.password, cast(str, user.password_hash)):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_session_token(cast(int, user.id))
        response.set_cookie(
            key="session",
            value=token,
            httponly=True,
            samesite=COOKIE_SAMESITE,
            secure=COOKIE_SECURE,
            max_age=60 * 60 * 24 * 7
        )

        return UserResponse(id=cast(int, user.id), email=cast(str, user.email), name=cast(str, user.name))
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

# ============== Entry Endpoints ==============

@app.get("/api/entries", response_model=list[EntryResponse])
def get_entries(
    group_id: int,
    entry_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get entries for a group, optionally filtered by date.

    Args:
        group_id: The group to get entries for
        entry_date: Optional date filter (YYYY-MM-DD format)

    Returns:
        List of EntryResponse objects

    Errors:
        401: Not authenticated
        403: Not a member of this group
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

        query = db.query(Entry).filter(Entry.group_id == group_id)

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current streak (consecutive days with all 3 sections completed) for a user in a group.

    Returns:
        StreakResponse with streak count and last complete date

    Errors:
        401: Not authenticated
        403: Not a member of this group
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

        # Get all complete days (3 sections) for this user in this group
        complete_days = (
            db.query(Entry.date)
            .filter(
                Entry.user_id == current_user.id,
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the history of completed sections for a user in a group.

    Args:
        group_id: The group to get history for
        days: Number of days to look back (default 30, max 365)

    Returns:
        List of HistoryDay objects sorted by date descending

    Errors:
        400: Invalid days parameter
        401: Not authenticated
        403: Not a member of this group
        404: Group not found
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

        start_date = date.today() - timedelta(days=days)

        entries = db.query(Entry).filter(
            Entry.user_id == current_user.id,
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
