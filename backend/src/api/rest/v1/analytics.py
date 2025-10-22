"""REST v1 analytics endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from core.database import get_db
from core.security import get_current_user
from services.analytics import get_group_analytics, get_global_analytics
from models.user import User

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
    # TODO: Add permission check - user should be group admin or member
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
    # Check if user is Super Admin
    if not hasattr(user, "role") or user.role.name != "SUPER_ADMIN":
        return {"error": "Super Admin access required"}
    analytics = get_global_analytics(db, start_date, end_date)
    return analytics
