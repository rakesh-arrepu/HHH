import strawberry
from typing import List, Optional, cast
from datetime import date
from dataclasses import dataclass

from core.database import session_scope
from services.entry import (
  list_entries_today as svc_list_entries_today,
  create_entry as svc_create_entry,
  update_entry as svc_update_entry,
  soft_delete_entry as svc_soft_delete_entry,
)
from models.entry import SectionEntry as SectionEntryModel, SectionType as ModelSectionType
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


@strawberry.input
class CreateEntryInput:
  user_id: str
  group_id: str
  section_type: SectionType
  content: str
  entry_date: Optional[date] = None

@strawberry.input
class UpdateEntryInput:
  content: Optional[str] = None
  section_type: Optional[SectionType] = None


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


@strawberry.type
class Mutation:
  @strawberry.mutation
  def create_entry(self, input: CreateEntryInput) -> Entry:
    with session_scope() as db:
      m = svc_create_entry(
        db,
        user_id=input.user_id,
        group_id=input.group_id,
        section_type=ModelSectionType(input.section_type.value),
        content=input.content,
        entry_date=input.entry_date,
      )
      return to_entry_type(m)

  @strawberry.mutation
  def update_entry(self, id: str, input: UpdateEntryInput) -> Entry:
    with session_scope() as db:
      m = svc_update_entry(
        db,
        entry_id=id,
        content=input.content if (input and input.content is not None) else None,
        section_type=ModelSectionType(input.section_type.value) if (input and input.section_type is not None) else None,
      )
      return to_entry_type(m)

  @strawberry.mutation
  def delete_entry(self, id: str) -> bool:
    with session_scope() as db:
      return svc_soft_delete_entry(db, entry_id=id)

schema = strawberry.Schema(query=Query, mutation=Mutation)
