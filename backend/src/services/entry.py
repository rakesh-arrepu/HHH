from datetime import date, datetime, timezone, timedelta
from typing import List, Optional, Any, cast

from sqlalchemy.orm import Session

from models.entry import SectionEntry, SectionType


def list_entries_today(
    db: Session, user_id: str, group_id: Optional[str] = None
) -> List[SectionEntry]:
    """
    Return today's active entries for a user (optionally scoped to a group).
    Service enforces soft-delete and per-day filter; DB uniqueness is partial in Postgres.
    """
    q = (
        db.query(SectionEntry)
        .filter(
            SectionEntry.user_id == user_id,
            SectionEntry.entry_date == date.today(),
            SectionEntry.deleted_at.is_(None),
        )
    )
    if group_id:
        q = q.filter(SectionEntry.group_id == group_id)
    return q.all()


def _get_entry_by_id(db: Session, entry_id: str) -> SectionEntry:
    e = db.query(SectionEntry).filter(
        SectionEntry.id == entry_id,
        SectionEntry.deleted_at.is_(None),
    ).first()
    if not e:
        raise ValueError("Entry not found or deleted")
    return e


def create_entry(
    db: Session,
    *,
    user_id: str,
    group_id: str,
    section_type: SectionType,
    content: str,
    entry_date: Optional[date] = None,
) -> SectionEntry:
    """Create a new daily entry; enforce one active entry per (user, group, section, date)."""
    edate = entry_date or date.today()
    if not content or not content.strip():
        raise ValueError("Content must not be empty")

    # Enforce unique active entry among same (user, group, section, date)
    existing = (
        db.query(SectionEntry)
        .filter(
            SectionEntry.user_id == user_id,
            SectionEntry.group_id == group_id,
            SectionEntry.section_type == section_type,
            SectionEntry.entry_date == edate,
            SectionEntry.deleted_at.is_(None),
        )
        .first()
    )
    if existing:
        raise ValueError("Entry already exists for this section today")

    e = SectionEntry(
        user_id=user_id,
        group_id=group_id,
        section_type=section_type,
        content=content.strip(),
        entry_date=edate,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


def update_entry(
    db: Session,
    *,
    entry_id: str,
    content: Optional[str] = None,
    section_type: Optional[SectionType] = None,
) -> SectionEntry:
    """Update content and/or section_type; increment edit_count."""
    e = _get_entry_by_id(db, entry_id)

    if content is not None:
        if not content.strip():
            raise ValueError("Content must not be empty")
        cast(Any, e).content = content.strip()
        current_edits: int = int((cast(Any, e).edit_count or 0))
        cast(Any, e).edit_count = current_edits + 1

    if section_type is not None:
        cast(Any, e).section_type = section_type

    db.add(e)
    db.commit()
    db.refresh(e)
    return e


def soft_delete_entry(db: Session, *, entry_id: str) -> bool:
    """Soft delete by setting deleted_at."""
    e = _get_entry_by_id(db, entry_id)
    cast(Any, e).deleted_at = datetime.now(timezone.utc)
    db.add(e)
    db.commit()
    return True


def list_user_entries(
    db: Session, user_id: str, group_id: Optional[str] = None, limit: int = 50, offset: int = 0
) -> List[SectionEntry]:
    """List all active entries for a user, optionally scoped to group, with pagination."""
    q = db.query(SectionEntry).filter(
        SectionEntry.user_id == user_id,
        SectionEntry.deleted_at.is_(None),
    ).order_by(SectionEntry.entry_date.desc(), SectionEntry.created_at.desc())
    if group_id:
        q = q.filter(SectionEntry.group_id == group_id)
    return q.offset(offset).limit(limit).all()


def get_entry_by_id(db: Session, entry_id: str) -> SectionEntry:
    """Get entry by ID (public alias for internal function)."""
    return _get_entry_by_id(db, entry_id)


def get_daily_progress(
    db: Session, user_id: str, date: date, group_id: Optional[str] = None
) -> dict:
    """Get progress stats for a specific date."""
    q = db.query(SectionEntry).filter(
        SectionEntry.user_id == user_id,
        SectionEntry.entry_date == date,
        SectionEntry.deleted_at.is_(None),
    )
    if group_id:
        q = q.filter(SectionEntry.group_id == group_id)

    entries = q.all()
    total_entries = len(entries)
    completed_sections = len(set(e.section_type for e in entries))
    total_sections = len(SectionType)  # Assuming 3 sections: Health, Happiness, Hela

    return {
        "date": date.isoformat(),
        "total_entries": total_entries,
        "completed_sections": completed_sections,
        "total_sections": total_sections,
        "progress_percentage": (completed_sections / total_sections * 100) if total_sections > 0 else 0,
        "entries": entries,
    }


def calculate_streak(db: Session, user_id: str, group_id: Optional[str] = None) -> int:
    """Calculate current streak of consecutive days with at least one entry."""
    # Get all entry dates for user (and group if specified), ordered by date desc
    q = db.query(SectionEntry.entry_date).filter(
        SectionEntry.user_id == user_id,
        SectionEntry.deleted_at.is_(None),
    ).distinct(SectionEntry.entry_date).order_by(SectionEntry.entry_date.desc())

    if group_id:
        q = q.filter(SectionEntry.group_id == group_id)

    entry_dates = [row[0] for row in q.all()]
    if not entry_dates:
        return 0

    today = date.today()
    streak = 0
    current_date = today

    # Check if today has entries
    if today in entry_dates:
        streak += 1
        current_date -= timedelta(days=1)
    else:
        return 0  # Streak broken if no entry today

    # Count consecutive days backwards
    while current_date in entry_dates:
        streak += 1
        current_date -= timedelta(days=1)

    return streak


def restore_entry(db: Session, *, entry_id: str, user_id: str) -> SectionEntry:
    """Restore a soft-deleted entry (only by the owner)."""
    e = db.query(SectionEntry).filter(
        SectionEntry.id == entry_id,
        SectionEntry.user_id == user_id,  # Ensure ownership
    ).first()

    if not e:
        raise ValueError("Entry not found")
    if e.deleted_at is None:
        raise ValueError("Entry is not deleted")

    cast(Any, e).deleted_at = None
    db.add(e)
    db.commit()
    db.refresh(e)
    return e
