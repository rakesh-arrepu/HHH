from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from models.entry import SectionEntry


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
