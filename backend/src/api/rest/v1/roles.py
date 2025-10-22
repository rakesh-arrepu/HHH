"""REST v1 roles endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from services.role import promote_to_group_admin, demote_to_user

router = APIRouter()

class PromoteRequest(BaseModel):
    userId: str
    groupId: str
    confirm: bool = False

class DemoteRequest(BaseModel):
    userId: str
    groupId: str
    confirm: bool = False

@router.post("/promote")
def promote_user_to_admin(
    payload: PromoteRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Promote a user to Group Admin for a group (Super Admin only)."""
    if not payload.confirm:
        return {"error": "Confirmation required"}
    try:
        message = promote_to_group_admin(db, str(user.id), payload.userId, payload.groupId)
        return {"message": message}
    except Exception as e:
        return {"error": str(e)}

@router.post("/demote")
def demote_admin_to_user(
    payload: DemoteRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Demote a Group Admin to User (Super Admin only)."""
    if not payload.confirm:
        return {"error": "Confirmation required"}
    try:
        message = demote_to_user(db, str(user.id), payload.userId, payload.groupId)
        return {"message": message}
    except Exception as e:
        return {"error": str(e)}
