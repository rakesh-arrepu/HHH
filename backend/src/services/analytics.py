from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional

from models.entry import SectionEntry
from models.user import User
from models.group import Group
from models.group_member import GroupMember
from models.audit import AuditLog


def get_group_analytics(db: Session, group_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
    """Get analytics for a specific group."""
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    # Basic group stats
    member_count = db.query(GroupMember).filter_by(group_id=group_id, deleted_at=None).count()
    entry_count = db.query(SectionEntry).filter(
        SectionEntry.group_id == group_id,
        SectionEntry.deleted_at.is_(None),
        SectionEntry.entry_date.between(start_date, end_date)
    ).count()

    # Daily activity over the period
    daily_entries = db.query(
        SectionEntry.entry_date,
        sql_func.count(SectionEntry.id).label('count')
    ).filter(
        SectionEntry.group_id == group_id,
        SectionEntry.deleted_at.is_(None),
        SectionEntry.entry_date.between(start_date, end_date)
    ).group_by(SectionEntry.entry_date).all()

    # User participation
    active_users = db.query(
        sql_func.count(sql_func.distinct(SectionEntry.user_id))
    ).filter(
        SectionEntry.group_id == group_id,
        SectionEntry.deleted_at.is_(None),
        SectionEntry.entry_date.between(start_date, end_date)
    ).scalar()

    # Streaks and engagement
    avg_streak = db.query(
        sql_func.avg(
            db.query(sql_func.count(SectionEntry.id))
            .filter(
                SectionEntry.user_id == User.id,
                SectionEntry.group_id == group_id,
                SectionEntry.deleted_at.is_(None)
            )
            .correlate(User)
            .as_scalar()
        )
    ).filter(User.deleted_at.is_(None)).scalar() or 0

    return {
        "group_id": group_id,
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "member_count": member_count,
        "total_entries": entry_count,
        "active_users": active_users,
        "avg_streak": float(avg_streak),
        "daily_activity": [{"date": d.isoformat(), "entries": c} for d, c in daily_entries],
    }


def get_global_analytics(db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
    """Get system-wide analytics (Super Admin only)."""
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    # System stats
    total_users = db.query(User).filter_by(deleted_at=None).count()
    total_groups = db.query(Group).filter_by(deleted_at=None).count()
    total_entries = db.query(SectionEntry).filter(
        SectionEntry.deleted_at.is_(None),
        SectionEntry.entry_date.between(start_date, end_date)
    ).count()

    # New signups in period
    new_users = db.query(User).filter(
        User.created_at.between(start_date, end_date),
        User.deleted_at.is_(None)
    ).count()

    # Active users (users with entries in period)
    active_users = db.query(sql_func.count(sql_func.distinct(SectionEntry.user_id))).filter(
        SectionEntry.deleted_at.is_(None),
        SectionEntry.entry_date.between(start_date, end_date)
    ).scalar()

    # Group activity
    active_groups = db.query(sql_func.count(sql_func.distinct(SectionEntry.group_id))).filter(
        SectionEntry.deleted_at.is_(None),
        SectionEntry.entry_date.between(start_date, end_date)
    ).scalar()

    return {
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "total_users": total_users,
        "total_groups": total_groups,
        "total_entries": total_entries,
        "new_users": new_users,
        "active_users": active_users,
        "active_groups": active_groups,
        "engagement_rate": (active_users / total_users * 100) if total_users > 0 else 0,
    }


def flag_entry(db: Session, entry_id: str, reason: str, flagged_by: str) -> SectionEntry:
    """Flag an entry for moderation."""
    entry = db.query(SectionEntry).filter_by(id=entry_id, deleted_at=None).first()
    if not entry:
        raise ValueError("Entry not found")

    entry.is_flagged = True  # type: ignore
    entry.flagged_reason = reason  # type: ignore
    db.commit()
    db.refresh(entry)

    # Log audit event
    audit = AuditLog(
        user_id=flagged_by,
        action="flag_entry",
        resource_type="entry",
        resource_id=entry_id,
        metadata={"reason": reason}
    )
    db.add(audit)
    db.commit()

    return entry


def unflag_entry(db: Session, entry_id: str, unflagged_by: str) -> SectionEntry:
    """Remove flag from an entry."""
    entry = db.query(SectionEntry).filter_by(id=entry_id, deleted_at=None).first()
    if not entry:
        raise ValueError("Entry not found")

    entry.is_flagged = False  # type: ignore
    entry.flagged_reason = None  # type: ignore
    db.commit()
    db.refresh(entry)

    # Log audit event
    audit = AuditLog(
        user_id=unflagged_by,
        action="unflag_entry",
        resource_type="entry",
        resource_id=entry_id
    )
    db.add(audit)
    db.commit()

    return entry


def get_audit_logs(db: Session, limit: int = 50, offset: int = 0, user_id: Optional[str] = None,
                   action: Optional[str] = None, resource_type: Optional[str] = None) -> List[AuditLog]:
    """Get audit logs with optional filtering."""
    query = db.query(AuditLog)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)

    return query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()


def log_audit_event(db: Session, user_id: str, action: str, resource_type: str,
                   resource_id: str, metadata: Optional[Dict[str, Any]] = None,
                   ip_address: Optional[str] = None) -> AuditLog:
    """Log an audit event."""
    audit = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata=metadata,
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit
