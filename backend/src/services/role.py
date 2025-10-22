from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.user import User
from models.group import Group
from models.role import Role

def promote_to_group_admin(db: Session, super_admin_id: str, user_id: str, group_id: str) -> str:
    """
    Promote a user to Group Admin for a specific group.
    - Only Super Admin can perform this.
    - Demotes existing Group Admin to User.
    - Sets new user as Group Admin and admin of the group.
    """
    # Verify Super Admin
    super_admin = db.query(User).filter_by(id=super_admin_id, deleted_at=None).first()
    if not super_admin or not super_admin.role or super_admin.role.name != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Only Super Admin can promote users.")

    # Get target user and group
    user = db.query(User).filter_by(id=user_id, deleted_at=None).first()
    group = db.query(Group).filter_by(id=group_id, deleted_at=None).first()
    if not user or not group:
        raise HTTPException(status_code=404, detail="User or group not found.")

    # Get Group Admin role
    group_admin_role = db.query(Role).filter_by(name="GROUP_ADMIN").first()
    user_role = db.query(Role).filter_by(name="USER").first()
    if not group_admin_role or not user_role:
        raise HTTPException(status_code=500, detail="Role configuration error.")

    # Demote existing admin if any
    if group.admin_id is not None:
        existing_admin = db.query(User).filter_by(id=group.admin_id).first()
        if existing_admin:
            existing_admin.role_id = user_role.id

    # Promote new user
    user.role_id = group_admin_role.id
    group.admin_id = user.id

    db.commit()
    return f"User {user.name} promoted to Group Admin for group {group.name}."

def demote_to_user(db: Session, super_admin_id: str, user_id: str, group_id: str) -> str:
    """
    Demote a Group Admin to User.
    - Only Super Admin can perform this.
    - Only affects the specified group.
    """
    # Verify Super Admin
    super_admin = db.query(User).filter_by(id=super_admin_id, deleted_at=None).first()
    if not super_admin or not super_admin.role or super_admin.role.name != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Only Super Admin can demote users.")

    # Get target user and group
    user = db.query(User).filter_by(id=user_id, deleted_at=None).first()
    group = db.query(Group).filter_by(id=group_id, deleted_at=None).first()
    if not user or not group:
        raise HTTPException(status_code=404, detail="User or group not found.")

    # Check if user is admin of this group
    if group.admin_id != user.id: # type: ignore
        raise HTTPException(status_code=400, detail="User is not admin of this group.")

    # Demote to User
    user_role = db.query(Role).filter_by(name="USER").first()
    if not user_role:
        raise HTTPException(status_code=500, detail="Role configuration error.")

    user.role_id = user_role.id
    group.admin_id = None  # type: ignore # No admin for now, or assign another?

    db.commit()
    return f"User {user.name} demoted to User for group {group.name}."

def soft_delete_user(db: Session, super_admin_id: str, user_id: str) -> str:
    """
    Soft delete a user (Super Admin only).
    """
    super_admin = db.query(User).filter_by(id=super_admin_id, deleted_at=None).first()
    if not super_admin or not super_admin.role or super_admin.role.name != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Only Super Admin can delete users.")

    user = db.query(User).filter_by(id=user_id, deleted_at=None).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Soft delete user (and cascade to entries, memberships)
    from datetime import datetime, timezone
    user.deleted_at = datetime.now(timezone.utc)  # type: ignore
    # Additional cascade logic can be added here

    db.commit()
    return f"User {user.name} soft deleted."
