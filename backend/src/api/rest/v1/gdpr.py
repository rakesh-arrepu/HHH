"""GDPR compliance endpoints."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Any

from core.database import get_db
from core.security import get_current_user
from services.gdpr import export_user_data, delete_user_account
from core.exceptions import error_response
from api.middleware.rate_limit import check_rate_limit, make_rate_limit_key

router = APIRouter()

# Rate limit config
GDPR_EXPORT_LIMIT = 2
GDPR_EXPORT_WINDOW = 3600  # seconds

@router.get("/export")
def export_user_data_endpoint(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)) -> Any:
    """Export user's personal data in GDPR-compliant format."""
    # Rate limit
    key = make_rate_limit_key(
        "gdpr_export",
        user_id=str(getattr(user, "id", "")),
        client_ip=getattr(getattr(request, "client", None), "host", None),
    )
    if not check_rate_limit(key, GDPR_EXPORT_LIMIT, GDPR_EXPORT_WINDOW):
        return error_response(
            429,
            "Rate limit exceeded",
            code="ERR_RATE_LIMIT",
            details={"endpoint": "gdpr.export", "limit": GDPR_EXPORT_LIMIT, "window": GDPR_EXPORT_WINDOW},
            request=request,
        )
    try:
        data = export_user_data(db, str(user.id))
        return data
    except Exception as e:
        return error_response(
            500,
            f"Export failed: {str(e)}",
            code="ERR_GDPR_EXPORT_FAILED",
            details={"endpoint": "gdpr.export"},
            request=request,
        )

@router.delete("/delete")
def delete_user_account_endpoint(request: Request, confirm: bool = False, db: Session = Depends(get_db), user=Depends(get_current_user)) -> Any:
    """Completely delete user account and all associated data."""
    if not confirm:
        return error_response(
            400,
            "Confirmation required. Set confirm=true to proceed.",
            code="ERR_CONFIRMATION_REQUIRED",
            details={"endpoint": "gdpr.delete"},
            request=request,
        )
    try:
        message = delete_user_account(db, str(user.id))
        return {"message": message}
    except Exception as e:
        return error_response(
            500,
            f"Account deletion failed: {str(e)}",
            code="ERR_GDPR_DELETE_FAILED",
            details={"endpoint": "gdpr.delete"},
            request=request,
        )
