from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import Optional, Literal, cast
import os
from fastapi import FastAPI, Depends, HTTPException, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine, get_db, Base
from models import User, Group, GroupMember, Entry # type: ignore
from auth import hash_password, verify_password, create_session_token, verify_session_token, create_password_reset_token, verify_password_reset_token

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Daily Tracker API")

# CORS for frontend
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174")
ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()]

is_production = os.getenv("RENDER", "").lower() == "true"

if is_production:
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== Pydantic Schemas ==============

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str

class GroupCreate(BaseModel):
    name: str

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
    date: Optional[date] = None

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
    # Check if email exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        name=user_data.name
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

@app.post("/api/auth/login", response_model=UserResponse)
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
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

@app.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie(key="session")
    return {"message": "Logged out"}

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(id=cast(int, current_user.id), email=cast(str, current_user.email), name=cast(str, current_user.name))

# ============== Password Reset Endpoints ==============

@app.post("/api/auth/password/forgot")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Issue a time-limited password reset token for a given email.
    Always return a generic success message. For local/dev, also return the token.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Do not reveal whether the email exists
        return {"message": "If account exists, a reset link was sent."}
    token = create_password_reset_token(payload.email)
    # In production you would email this token. For dev, return it for convenience.
    return {"message": "If account exists, a reset link was sent.", "reset_token": token}

@app.post("/api/auth/password/reset")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password using a valid reset token. Overwrites the user's password hash.
    """
    email = verify_password_reset_token(payload.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(payload.password)  # type: ignore[assignment]
    db.add(user)
    db.commit()

    return {"message": "Password has been reset successfully."}

# ============== Group Endpoints ==============

@app.get("/api/groups", response_model=list[GroupResponse])
def list_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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

@app.post("/api/groups", response_model=GroupResponse)
def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    group = Group(name=group_data.name, owner_id=current_user.id)
    db.add(group)
    db.commit()
    db.refresh(group)

    # Add owner as member too
    member = GroupMember(group_id=group.id, user_id=current_user.id)
    db.add(member)
    db.commit()

    return GroupResponse(id=cast(int, group.id), name=cast(str, group.name), owner_id=cast(int, group.owner_id), is_owner=True)

@app.get("/api/groups/{group_id}/members", response_model=list[MemberResponse])
def list_members(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user has access to group
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()

    if not is_member and group.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not a member of this group")

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

@app.post("/api/groups/{group_id}/members", response_model=MemberResponse)
def add_member(
    group_id: int,
    member_data: MemberAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can add members")

    user = db.query(User).filter(User.email == member_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already a member")

    member = GroupMember(group_id=group_id, user_id=user.id)
    db.add(member)
    db.commit()
    db.refresh(member)

    return MemberResponse(id=cast(int, member.id), user_id=cast(int, user.id), name=cast(str, user.name), email=cast(str, user.email))

@app.delete("/api/groups/{group_id}/members/{user_id}")
def remove_member(
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can remove members")

    if user_id == group.owner_id:
        raise HTTPException(status_code=400, detail="Cannot remove owner from group")

    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    ).first()

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    db.delete(member)
    db.commit()

    return {"message": "Member removed"}

# ============== Entry Endpoints ==============

@app.get("/api/entries", response_model=list[EntryResponse])
def get_entries(
    group_id: int,
    entry_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify membership
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()

    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this group")

    query = db.query(Entry).filter(Entry.group_id == group_id)

    if entry_date:
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

@app.post("/api/entries", response_model=EntryResponse)
def create_or_update_entry(
    entry_data: EntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate section
    if entry_data.section not in ["health", "happiness", "hela"]:
        raise HTTPException(status_code=400, detail="Invalid section")

    # Verify membership
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == entry_data.group_id,
        GroupMember.user_id == current_user.id
    ).first()

    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this group")

    entry_date = entry_data.date or date.today()

    # Check for existing entry
    existing = db.query(Entry).filter(
        Entry.user_id == current_user.id,
        Entry.group_id == entry_data.group_id,
        Entry.section == entry_data.section,
        Entry.date == entry_date
    ).first()

    if existing:
        # Update existing
        existing.content = entry_data.content
        existing.updated_at = datetime.utcnow()
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

# ============== Analytics Endpoints ==============

@app.get("/api/analytics/streak", response_model=StreakResponse)
def get_streak(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify membership
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()

    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this group")

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

@app.get("/api/analytics/history", response_model=list[HistoryDay])
def get_history(
    group_id: int,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify membership
    is_member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()

    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this group")

    start_date = date.today() - timedelta(days=days)

    entries = db.query(Entry).filter(
        Entry.user_id == current_user.id,
        Entry.group_id == group_id,
        Entry.date >= start_date
    ).all()

    # Group by date
    by_date = {}
    for e in entries:
        if e.date not in by_date:
            by_date[e.date] = []
        by_date[e.date].append(e.section)

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

# ============== Health Check ==============

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
