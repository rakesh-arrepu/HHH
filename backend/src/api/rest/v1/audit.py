"""Audit logs REST endpoints (Super Admin only)."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional

from core.database import get_db
from core.security import get_current_user
from services.analytics import get_audit_logs, log_audit_event
from core.exceptions import error_response

router = APIRouter()


@router.get("/logs")
def get_audit_logs_endpoint(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    userId: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    resourceType: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> Any:
    """
    Return audit logs with optional filtering.
    Access: Super Admin only.
    """
    # Super Admin check
    role_name = getattr(getattr(user, "role", None), "name", None)
    if role_name != "SUPER_ADMIN":
        try:
            log_audit_event(
                db,
                str(getattr(user, "id", "")),
                "unauthorized_access",
                "audit_logs",
                "-",
                {"endpoint": "audit.logs"},
                getattr(getattr(request, "client", None), "host", None),
            )
        except Exception:
            pass
        return error_response(
            403,
            "Super Admin access required",
            code="ERR_SUPERADMIN_REQUIRED",
            details={"endpoint": "audit.logs"},
            request=request,
        )

    try:
        logs = get_audit_logs(
            db,
            limit=limit,
            offset=offset,
            user_id=userId,
            action=action,
            resource_type=resourceType,
        )
        def to_dict(log) -> Dict[str, Any]:
            meta = getattr(log, "metadata", None)
            if meta is None:
                # Model attribute is named 'meta', DB column is 'metadata'
                meta = getattr(log, "meta", None)
            return {
                "id": str(getattr(log, "id", "")),
                "user_id": str(getattr(log, "user_id", "")),
                "action": getattr(log, "action", ""),
                "resource_type": getattr(log, "resource_type", ""),
                "resource_id": str(getattr(log, "resource_id", "")),
                "metadata": meta,
                "ip_address": getattr(log, "ip_address", None),
                "created_at": str(getattr(log, "created_at", "")),
            }

        return [to_dict(l) for l in logs]
    except Exception as e:
        try:
            log_audit_event(
                db,
                str(getattr(user, "id", "")),
                "audit_logs_failed",
                "audit_logs",
                "-",
                {"error": str(e)},
                getattr(getattr(request, "client", None), "host", None),
            )
        except Exception:
            pass
        return error_response(
            500,
            f"Failed to retrieve audit logs: {str(e)}",
            code="ERR_AUDIT_LOGS_FAILED",
            details={"endpoint": "audit.logs"},
            request=request,
        )
