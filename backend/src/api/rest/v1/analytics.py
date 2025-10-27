"""REST v1 analytics endpoints."""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from core.exceptions import NotFoundError, ForbiddenError

from core.database import get_db
from core.security import get_current_user
from services.analytics import get_group_analytics, get_global_analytics
from models.user import User
from models.group import Group
from models.group_member import GroupMember

router = APIRouter()

@router.get("/group/{group_id}")
def get_group_analytics_endpoint(
    group_id: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get analytics for a specific group."""
    # Permission: user must be group admin or member
    group = db.query(Group).filter_by(id=group_id, deleted_at=None).first()
    if not group:
        # Standardized envelope: ERR_NOT_FOUND
        raise NotFoundError("Group not found")

    is_admin = getattr(group, "admin_id", None) == str(user.id)
    is_member = db.query(GroupMember).filter_by(group_id=group_id, user_id=str(user.id), deleted_at=None).first() is not None
    if not (is_admin or is_member):
        # Standardized envelope: ERR_FORBIDDEN
        raise ForbiddenError("Not authorized to view this group's analytics")

    analytics = get_group_analytics(db, group_id, start_date, end_date)
    return analytics

@router.get("/global")
def get_global_analytics_endpoint(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get system-wide analytics (Super Admin only)."""
    # Check if user is Super Admin (guard against missing/None role)
    role_name = getattr(getattr(user, "role", None), "name", None)
    if role_name != "SUPER_ADMIN":
        # Standardized envelope: ERR_FORBIDDEN
        raise ForbiddenError("Super Admin access required")
    analytics = get_global_analytics(db, start_date, end_date)
    return analytics
