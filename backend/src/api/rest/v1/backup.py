"""Backup management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from core.database import get_db
from core.security import get_current_user
from services.backup import trigger_backup, get_backup_logs, get_backup_stats

router = APIRouter()

@router.post("/trigger")
def trigger_backup_endpoint(db: Session = Depends(get_db), user=Depends(get_current_user)) -> Dict[str, Any]:
    """Trigger a database backup (Super Admin only)."""
    # Check if user is Super Admin
    if not hasattr(user, "role") or user.role.name != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Super Admin access required")

    try:
        result = trigger_backup(db, str(user.id))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")

@router.get("/logs")
def get_backup_logs_endpoint(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get backup operation logs (Super Admin only)."""
    # Check if user is Super Admin
    if not hasattr(user, "role") or user.role.name != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Super Admin access required")

    try:
        logs = get_backup_logs(db, limit, offset)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve backup logs: {str(e)}")

@router.get("/stats")
def get_backup_stats_endpoint(db: Session = Depends(get_db), user=Depends(get_current_user)) -> Dict[str, Any]:
    """Get backup statistics (Super Admin only)."""
    # Check if user is Super Admin
    if not hasattr(user, "role") or user.role.name != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Super Admin access required")

    try:
        stats = get_backup_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve backup stats: {str(e)}")
