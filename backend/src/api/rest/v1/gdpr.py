"""GDPR compliance endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from core.database import get_db
from core.security import get_current_user
from services.gdpr import export_user_data, delete_user_account

router = APIRouter()

@router.get("/export")
def export_user_data_endpoint(db: Session = Depends(get_db), user=Depends(get_current_user)) -> Dict[str, Any]:
    """Export user's personal data in GDPR-compliant format."""
    try:
        data = export_user_data(db, str(user.id))
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.delete("/delete")
def delete_user_account_endpoint(confirm: bool = False, db: Session = Depends(get_db), user=Depends(get_current_user)) -> Dict[str, str]:
    """Completely delete user account and all associated data."""
    if not confirm:
        raise HTTPException(status_code=400, detail="Confirmation required. Set confirm=true to proceed.")
    try:
        message = delete_user_account(db, str(user.id))
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Account deletion failed: {str(e)}")
