from datetime import date, datetime, timezone
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
