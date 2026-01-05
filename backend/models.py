from __future__ import annotations
from datetime import datetime, date
from typing import Optional
from sqlalchemy import ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    owned_groups: Mapped[list["Group"]] = relationship("Group", back_populates="owner")
    memberships: Mapped[list["GroupMember"]] = relationship("GroupMember", back_populates="user")
    entries: Mapped[list["Entry"]] = relationship("Entry", back_populates="user")
    health_activities: Mapped[list["HealthActivity"]] = relationship("HealthActivity", back_populates="user")
    activity_favorites: Mapped[list["UserActivityFavorite"]] = relationship("UserActivityFavorite", back_populates="user")


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    owner: Mapped["User"] = relationship("User", back_populates="owned_groups")
    members: Mapped[list["GroupMember"]] = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    entries: Mapped[list["Entry"]] = relationship("Entry", back_populates="group", cascade="all, delete-orphan")
    health_activities: Mapped[list["HealthActivity"]] = relationship("HealthActivity", back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    __tablename__ = "group_members"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    group: Mapped["Group"] = relationship("Group", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="memberships")

    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_group_user"),)


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    section: Mapped[str] = mapped_column(nullable=False)  # 'health', 'happiness', 'hela'
    content: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[date] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="entries")
    group: Mapped["Group"] = relationship("Group", back_populates="entries")

    __table_args__ = (
        UniqueConstraint("user_id", "group_id", "section", "date", name="uq_user_group_section_date"),
    )

class ActivityType(Base):
    """Predefined activity types catalog for Health section."""
    __tablename__ = "activity_types"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)  # "Walking", "Running"
    category: Mapped[str] = mapped_column(nullable=False)  # "cardio", "sports", "strength", etc.
    icon: Mapped[str] = mapped_column(nullable=False)  # Lucide icon name: "footprints"
    color: Mapped[str] = mapped_column(nullable=False)  # Tailwind color: "emerald"
    met_value: Mapped[float] = mapped_column(nullable=False)  # MET for calorie calculation
    default_duration: Mapped[int] = mapped_column(default=30)  # Default duration in minutes
    is_active: Mapped[bool] = mapped_column(default=True)  # Soft delete flag
    display_order: Mapped[int] = mapped_column(default=0)  # For sorting
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    activities: Mapped[list["HealthActivity"]] = relationship("HealthActivity", back_populates="activity_type")
    favorites: Mapped[list["UserActivityFavorite"]] = relationship("UserActivityFavorite", back_populates="activity_type")


class HealthActivity(Base):
    """User activity logs for Health section tracking."""
    __tablename__ = "health_activities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    activity_type_id: Mapped[int] = mapped_column(ForeignKey("activity_types.id"), nullable=False)
    date: Mapped[date] = mapped_column(nullable=False)
    duration: Mapped[Optional[int]] = mapped_column(nullable=True)  # Duration value
    duration_unit: Mapped[str] = mapped_column(default="minutes")  # "minutes" or "hours"
    distance: Mapped[Optional[float]] = mapped_column(nullable=True)  # Distance in km
    calories: Mapped[int] = mapped_column(nullable=False)  # Auto-calculated calories
    notes: Mapped[Optional[str]] = mapped_column(nullable=True)  # Optional notes
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="health_activities")
    group: Mapped["Group"] = relationship("Group", back_populates="health_activities")
    activity_type: Mapped["ActivityType"] = relationship("ActivityType", back_populates="activities")

    __table_args__ = (
        Index("idx_health_activities_user_date", "user_id", "date"),
        Index("idx_health_activities_group_date", "group_id", "date"),
    )


class UserActivityFavorite(Base):
    """User's favorite activities for quick-log feature."""
    __tablename__ = "user_activity_favorites"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    activity_type_id: Mapped[int] = mapped_column(ForeignKey("activity_types.id"), nullable=False)
    display_order: Mapped[int] = mapped_column(default=0)  # For sorting favorites
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="activity_favorites")
    activity_type: Mapped["ActivityType"] = relationship("ActivityType", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint("user_id", "activity_type_id", name="uq_user_activity_favorite"),
    )


# Explicit export list to satisfy static analyzers
__all__ = ("User", "Group", "GroupMember", "Entry", "ActivityType", "HealthActivity", "UserActivityFavorite")
