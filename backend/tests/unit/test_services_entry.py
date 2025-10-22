import os
import sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from datetime import date, timedelta
import pytest

from sqlalchemy.orm import Session

from services.entry import (
    create_entry,
    list_entries_today,
    update_entry,
    soft_delete_entry,
)
from models.entry import SectionType


def test_create_and_list_entries_today(db_session: Session, user_group):
    user_id, group_id = user_group

    # Initially empty
    entries = list_entries_today(db_session, user_id=user_id, group_id=group_id)
    assert entries == []

    # Create today's entry
    e = create_entry(
        db_session,
        user_id=user_id,
        group_id=group_id,
        section_type=SectionType.Health,
        content="  Walked 5k steps  ",  # whitespace should be trimmed
    )
    assert e.id
    assert e.content == "Walked 5k steps"
    assert e.entry_date == date.today()

    # Listed
    entries = list_entries_today(db_session, user_id=user_id, group_id=group_id)
    assert len(entries) == 1
    assert entries[0].id == e.id

    # Create entry for yesterday (should not appear in "today")
    e2 = create_entry(
        db_session,
        user_id=user_id,
        group_id=group_id,
        section_type=SectionType.Happiness,
        content="Had coffee",
        entry_date=date.today() - timedelta(days=1),
    )
    assert e2.entry_date != date.today()

    entries = list_entries_today(db_session, user_id=user_id, group_id=group_id)
    assert len(entries) == 1  # still only today's


def test_list_entries_today_group_filter(db_session: Session, user_group, group_factory):
    user_id, group_id = user_group
    other_group = group_factory().id

    # Create in group A
    e_a = create_entry(
        db_session,
        user_id=user_id,
        group_id=group_id,
        section_type=SectionType.Health,
        content="A",
    )
    # Create in group B
    e_b = create_entry(
        db_session,
        user_id=user_id,
        group_id=other_group,
        section_type=SectionType.Health,
        content="B",
    )

    # Scoped list per group
    a_entries = list_entries_today(db_session, user_id=user_id, group_id=group_id)
    b_entries = list_entries_today(db_session, user_id=user_id, group_id=other_group)

    assert len(a_entries) == 1 and a_entries[0].id == e_a.id
    assert len(b_entries) == 1 and b_entries[0].id == e_b.id


def test_duplicate_entry_same_day_raises(db_session: Session, user_group):
    user_id, group_id = user_group

    create_entry(
        db_session,
        user_id=user_id,
        group_id=group_id,
        section_type=SectionType.Health,
        content="One",
    )
    with pytest.raises(ValueError, match="already exists"):
        create_entry(
            db_session,
            user_id=user_id,
            group_id=group_id,
            section_type=SectionType.Health,
            content="Two",
        )


def test_create_entry_empty_content_raises(db_session: Session, user_group):
    user_id, group_id = user_group

    with pytest.raises(ValueError, match="must not be empty"):
        create_entry(
            db_session,
            user_id=user_id,
            group_id=group_id,
            section_type=SectionType.Health,
            content="   ",
        )


def test_update_entry_content_and_section_type(db_session: Session, user_group):
    user_id, group_id = user_group

    e = create_entry(
        db_session,
        user_id=user_id,
        group_id=group_id,
        section_type=SectionType.Health,
        content="Initial",
    )
    assert e.edit_count == 0

    e2 = update_entry(
        db_session,
        entry_id=e.id,
        content="  Updated Content  ",
        section_type=SectionType.Happiness,
    )
    assert e2.content == "Updated Content"
    assert e2.section_type == SectionType.Happiness
    assert e2.edit_count == 1  # incremented

    # Updating without content change doesn't bump count
    e3 = update_entry(
        db_session,
        entry_id=e.id,
        section_type=SectionType.Hela,
    )
    assert e3.edit_count == 1  # unchanged count


def test_update_entry_with_empty_content_raises(db_session: Session, user_group):
    user_id, group_id = user_group

    e = create_entry(
        db_session,
        user_id=user_id,
        group_id=group_id,
        section_type=SectionType.Health,
        content="Initial",
    )
    with pytest.raises(ValueError, match="must not be empty"):
        update_entry(db_session, entry_id=e.id, content="  ")


def test_soft_delete_excludes_from_list(db_session: Session, user_group):
    user_id, group_id = user_group

    e = create_entry(
        db_session,
        user_id=user_id,
        group_id=group_id,
        section_type=SectionType.Health,
        content="To delete",
    )
    assert soft_delete_entry(db_session, entry_id=e.id) is True

    # After soft delete, today's list should be empty
    entries = list_entries_today(db_session, user_id=user_id, group_id=group_id)
    assert entries == []
