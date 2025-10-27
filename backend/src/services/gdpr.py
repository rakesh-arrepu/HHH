"""GDPR compliance service for data export and account deletion."""

from sqlalchemy.orm import Session
from typing import Dict, Any, List
import json
from datetime import datetime, timezone

from models.user import User
from models.entry import SectionEntry
from models.group import Group
from models.group_member import GroupMember
from models.notification import Notification
from models.audit import AuditLog


def export_user_data(db: Session, user_id: str) -> Dict[str, Any]:
    """Export all user data in GDPR-compliant JSON format."""
    user = db.query(User).filter_by(id=user_id, deleted_at=None).first()
    if not user:
        raise ValueError("User not found")

    # Export user profile
    user_data = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role.name if user.role else None,
        "created_at": user.created_at.isoformat() if user.created_at is not None else None,  # type: ignore
        "updated_at": (getattr(user, "updated_at", None).isoformat() if getattr(user, "updated_at", None) else None),
        "is_2fa_enabled": getattr(user, "is_2fa_enabled", False),
        "timezone": getattr(user, "timezone", None),
    }

    # Export user's entries
    entries = db.query(SectionEntry).filter_by(user_id=user_id).all()
    entries_data = []
    for entry in entries:
        entries_data.append({
            "id": entry.id,
            "group_id": entry.group_id,
            "section_type": entry.section_type.value,
            "content": entry.content,
            "entry_date": entry.entry_date.isoformat(),
            "edit_count": entry.edit_count,
            "is_flagged": entry.is_flagged,
            "flagged_reason": entry.flagged_reason,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat() if entry.updated_at is not None else None,  # type: ignore
        })

    # Export user's group memberships
    memberships = db.query(GroupMember).filter_by(user_id=user_id).all()
    memberships_data = []
    for membership in memberships:
        memberships_data.append({
            "group_id": membership.group_id,
            "group_name": membership.group.name if membership.group else None,
            "joined_at": membership.joined_at.isoformat(),
            "day_streak": membership.day_streak,
        })

    # Export user's notifications
    notifications = db.query(Notification).filter_by(user_id=user_id).all()
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            "id": notification.id,
            "type": notification.type.value,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat(),
        })

    # Export audit logs for this user
    audit_logs = db.query(AuditLog).filter_by(user_id=user_id).all()
    audit_data = []
    for log in audit_logs:
        audit_data.append({
            "id": log.id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "metadata": log.metadata,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat(),
        })

    # Compile full export
    export_data = {
        "export_timestamp": datetime.now(timezone.utc).isoformat(),
        "user_profile": user_data,
        "entries": entries_data,
        "group_memberships": memberships_data,
        "notifications": notifications_data,
        "audit_logs": audit_data,
        "data_summary": {
            "total_entries": len(entries_data),
            "total_groups": len(memberships_data),
            "total_notifications": len(notifications_data),
            "total_audit_events": len(audit_data),
        }
    }

    return export_data


def delete_user_account(db: Session, user_id: str) -> str:
    """Permanently delete user account and all associated data."""
    user = db.query(User).filter_by(id=user_id, deleted_at=None).first()
    if not user:
        raise ValueError("User not found")

    # Count data before deletion for confirmation
    entries_count = db.query(SectionEntry).filter_by(user_id=user_id).count()
    memberships_count = db.query(GroupMember).filter_by(user_id=user_id).count()
    notifications_count = db.query(Notification).filter_by(user_id=user_id).count()

    # Delete in proper order (respecting foreign keys)
    # Delete entries
    db.query(SectionEntry).filter_by(user_id=user_id).delete()

    # Delete group memberships
    db.query(GroupMember).filter_by(user_id=user_id).delete()

    # Delete notifications
    db.query(Notification).filter_by(user_id=user_id).delete()

    # Delete audit logs
    db.query(AuditLog).filter_by(user_id=user_id).delete()

    # Finally delete the user
    db.delete(user)
    db.commit()

    return f"Account permanently deleted. Removed {entries_count} entries, {memberships_count} group memberships, {notifications_count} notifications, and all audit logs."
