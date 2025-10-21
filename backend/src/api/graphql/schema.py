import strawberry
from typing import List, Optional, cast
from datetime import date
from dataclasses import dataclass

from core.database import session_scope
from services.entry import list_entries_today as svc_list_entries_today
from models.entry import SectionEntry as SectionEntryModel
from enum import Enum as PyEnum


# Expose SectionType enum in GraphQL
@strawberry.enum
class SectionType(PyEnum):
  Health = "Health"
  Happiness = "Happiness"
  Hela = "Hela"


@strawberry.type
@dataclass
class Entry:
  id: str
  user_id: str
  group_id: str
  section_type: SectionType
  content: str
  entry_date: date
  edit_count: int
  is_flagged: bool
  flagged_reason: Optional[str]


def to_entry_type(m: SectionEntryModel) -> Entry:
  return Entry(
    id=cast(str, m.id),
    user_id=cast(str, m.user_id),
    group_id=cast(str, m.group_id),
    section_type=SectionType(m.section_type.value),
    content=cast(str, m.content),
    entry_date=cast(date, m.entry_date),
    edit_count=cast(int, m.edit_count),
    is_flagged=cast(bool, m.is_flagged),
    flagged_reason=cast(Optional[str], m.flagged_reason),
  )


@strawberry.type
class Query:
  @strawberry.field
  def health(self) -> str:
    return "ok"

  @strawberry.field
  def entries_today(self, user_id: str, group_id: Optional[str] = None) -> List[Entry]:
    # Minimal resolver wiring to service layer; uses a short-lived session scope
    with session_scope() as db:
      items = svc_list_entries_today(db, user_id=user_id, group_id=group_id)
      return [to_entry_type(i) for i in items]


schema = strawberry.Schema(query=Query)
