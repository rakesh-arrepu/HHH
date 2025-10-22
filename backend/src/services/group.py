from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from fastapi import HTTPException
from typing import Optional

from models.user import User
from models.group import Group
from models.group_member import GroupMember

def create_group(db: Session, name: str, description: str, timezone: str, admin_id: str) -> Group:
    """Create a new group with the given admin."""
    group = Group(name=name, description=description, timezone=timezone, admin_id=admin_id)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group

def update_group(db: Session, group_id: str, name: Optional[str] = None, description: Optional[str] = None, timezone: Optional[str] = None, admin_id: Optional[str] = None) -> Group:
    """Update group details."""
    group = db.query(Group).filter_by(id=group_id, deleted_at=None).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if name:
        group.name = name  # type: ignore
    if description:
        group.description = description  # type: ignore
    if timezone:
        group.timezone = timezone  # type: ignore
    if admin_id:
        group.admin_id = admin_id  # type: ignore
    db.commit()
    db.refresh(group)
    return group

def get_user_groups(db: Session, user_id: str) -> list[Group]:
    """Get all groups where user is a member."""
    memberships = db.query(GroupMember).filter_by(user_id=user_id, deleted_at=None).all()
    group_ids = [m.group_id for m in memberships]
    groups = db.query(Group).filter(Group.id.in_(group_ids), Group.deleted_at == None).all()
    return groups

def get_group_by_id(db: Session, group_id: str) -> Group:
    """Get group by ID with admin and members."""
    group = db.query(Group).filter_by(id=group_id, deleted_at=None).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

def add_member(db: Session, group_id: str, user_id: str) -> GroupMember:
    """Add user to group."""
    group = db.query(Group).filter_by(id=group_id, deleted_at=None).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    user = db.query(User).filter_by(id=user_id, deleted_at=None).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Check if already member
    existing = db.query(GroupMember).filter_by(group_id=group_id, user_id=user_id, deleted_at=None).first()
    if existing:
        raise HTTPException(status_code=409, detail="User already in group")
    member = GroupMember(group_id=group_id, user_id=user_id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

def remove_member(db: Session, group_id: str, user_id: str) -> str:
    """Remove user from group."""
    member = db.query(GroupMember).filter_by(group_id=group_id, user_id=user_id, deleted_at=None).first()
    if not member:
        raise HTTPException(status_code=404, detail="Membership not found")
    member.deleted_at = func.now()  # type: ignore
    db.commit()
    return f"User {user_id} removed from group {group_id}"

def list_groups(db: Session, limit: int = 10, offset: int = 0) -> list[Group]:
    """List all active groups (paginated)."""
    groups = db.query(Group).filter_by(deleted_at=None).offset(offset).limit(limit).all()
    return groups

def soft_delete_group(db: Session, group_id: str) -> str:
    """Soft delete a group."""
    group = db.query(Group).filter_by(id=group_id, deleted_at=None).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    group.deleted_at = func.now()  # type: ignore
    db.commit()
    return f"Group {group_id} soft deleted"
