"""Backup management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from core.database import get_db
from core.security import get_current_user
from services.backup import trigger_backup, get_backup_logs, get_backup_stats
from services.analytics import log_audit_event
from core.exceptions import error_response
from api.middleware.rate_limit import check_rate_limit, make_rate_limit_key

router = APIRouter()

# Rate limit config for backup trigger
BACKUP_TRIGGER_LIMIT = 2
BACKUP_TRIGGER_WINDOW = 3600  # seconds

@router.post("/trigger")
def trigger_backup_endpoint(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)) -> Any:
    """Trigger a database backup (Super Admin only)."""
    # Check if user is Super Admin
    if not hasattr(user, "role") or user.role.name != "SUPER_ADMIN":
        try:
            log_audit_event(
                db,
                str(getattr(user, "id", "")),
                "unauthorized_access",
                "backup",
                "-",
                {"endpoint": "trigger"},
                getattr(getattr(request, "client", None), "host", None),
            )
        except Exception:
            pass
        return error_response(403, "Super Admin access required", code="ERR_SUPERADMIN_REQUIRED", details={"endpoint": "trigger"}, request=request)

    # Rate limit (after role check)
    key = make_rate_limit_key(
        "backup_trigger",
        user_id=str(getattr(user, "id", "")),
        client_ip=getattr(getattr(request, "client", None), "host", None),
    )
    if not check_rate_limit(key, BACKUP_TRIGGER_LIMIT, BACKUP_TRIGGER_WINDOW):
        return error_response(
            429,
            "Rate limit exceeded",
            code="ERR_RATE_LIMIT",
            details={"endpoint": "backup.trigger", "limit": BACKUP_TRIGGER_LIMIT, "window": BACKUP_TRIGGER_WINDOW},
            request=request,
        )
    try:
        result = trigger_backup(db, str(user.id))
        return result
    except Exception as e:
        try:
            log_audit_event(
                db,
                str(getattr(user, "id", "")),
                "backup_trigger_failed",
                "backup",
                "-",
                {"error": str(e)},
                getattr(getattr(request, "client", None), "host", None),
            )
        except Exception:
            pass
        return error_response(500, f"Backup failed: {str(e)}", code="ERR_BACKUP_FAILED", details={"endpoint": "trigger"}, request=request)

@router.get("/logs")
def get_backup_logs_endpoint(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
) -> Any:
    """Get backup operation logs (Super Admin only)."""
    # Check if user is Super Admin
    if not hasattr(user, "role") or user.role.name != "SUPER_ADMIN":
        try:
            log_audit_event(
                db,
                str(getattr(user, "id", "")),
                "unauthorized_access",
                "backup_logs",
                "-",
                {"endpoint": "logs"},
                getattr(getattr(request, "client", None), "host", None),
            )
        except Exception:
            pass
        return error_response(403, "Super Admin access required", code="ERR_SUPERADMIN_REQUIRED", details={"endpoint": "logs"}, request=request)

    try:
        logs = get_backup_logs(db, limit, offset)
        return logs
    except Exception as e:
        try:
            log_audit_event(
                db,
                str(getattr(user, "id", "")),
                "backup_logs_failed",
                "backup",
                "-",
                {"error": str(e)},
                getattr(getattr(request, "client", None), "host", None),
            )
        except Exception:
            pass
        return error_response(500, f"Failed to retrieve backup logs: {str(e)}", code="ERR_BACKUP_LOGS_FAILED", details={"endpoint": "logs"}, request=request)

@router.get("/stats")
def get_backup_stats_endpoint(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)) -> Any:
    """Get backup statistics (Super Admin only)."""
    # Check if user is Super Admin
    if not hasattr(user, "role") or user.role.name != "SUPER_ADMIN":
        try:
            log_audit_event(
                db,
                str(getattr(user, "id", "")),
                "unauthorized_access",
                "backup_stats",
                "-",
                {"endpoint": "stats"},
                getattr(getattr(request, "client", None), "host", None),
            )
        except Exception:
            pass
        return error_response(403, "Super Admin access required", code="ERR_SUPERADMIN_REQUIRED", details={"endpoint": "stats"}, request=request)

    try:
        stats = get_backup_stats(db)
        return stats
    except Exception as e:
        try:
            log_audit_event(
                db,
                str(getattr(user, "id", "")),
                "backup_stats_failed",
                "backup",
                "-",
                {"error": str(e)},
                getattr(getattr(request, "client", None), "host", None),
            )
        except Exception:
            pass
        return error_response(500, f"Failed to retrieve backup stats: {str(e)}", code="ERR_BACKUP_STATS_FAILED", details={"endpoint": "stats"}, request=request)
