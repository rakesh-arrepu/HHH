"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2025-10-10

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enums
    section_type_enum = sa.Enum("Health", "Happiness", "Hela", name="section_type")
    notification_type_enum = sa.Enum(
        "incomplete_day", "streak_milestone", "admin_action", "moderation", name="notification_type"
    )
    backup_status_enum = sa.Enum("success", "failed", name="backup_status")

    section_type_enum.create(op.get_bind(), checkfirst=True)
    notification_type_enum.create(op.get_bind(), checkfirst=True)
    backup_status_enum.create(op.get_bind(), checkfirst=True)

    # roles
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=50), unique=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=True),
        sa.Column("totp_secret", sa.String(length=255), nullable=True),
        sa.Column("is_2fa_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # groups
    op.create_table(
        "groups",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("timezone", sa.String(length=50), nullable=False, server_default=sa.text("'Asia/Kolkata'")),
        sa.Column("admin_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # group_members
    op.create_table(
        "group_members",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("group_id", sa.String(length=36), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("day_streak", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_group_members_group_id", "group_members", ["group_id"], unique=False)
    op.create_index("ix_group_members_user_id", "group_members", ["user_id"], unique=False)
    # Partial unique index for active memberships (Postgres only)
    op.create_index(
        "uq_active_group_members",
        "group_members",
        ["group_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # section_entries
    op.create_table(
        "section_entries",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("group_id", sa.String(length=36), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("section_type", section_type_enum, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("edit_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_flagged", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("flagged_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_section_entries_user_id", "section_entries", ["user_id"], unique=False)
    op.create_index("ix_section_entries_group_id", "section_entries", ["group_id"], unique=False)
    # Partial unique index for active per-day entry (Postgres only)
    op.create_index(
        "uq_active_daily_section_entry",
        "section_entries",
        ["user_id", "group_id", "section_type", "entry_date"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # notifications
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", notification_type_enum, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"], unique=False)

    # audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=50), nullable=False),
        sa.Column("resource_id", sa.String(length=36), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"], unique=False)
    op.create_index("ix_audit_logs_resource_id", "audit_logs", ["resource_id"], unique=False)

    # backup_logs
    op.create_table(
        "backup_logs",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("backup_file", sa.String(length=255), nullable=False),
        sa.Column("backup_size", sa.BigInteger(), nullable=False),
        sa.Column("status", backup_status_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    # Drop in reverse order
    op.drop_table("backup_logs")

    op.drop_index("ix_audit_logs_resource_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_user_id", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")

    op.drop_index("uq_active_daily_section_entry", table_name="section_entries")
    op.drop_index("ix_section_entries_group_id", table_name="section_entries")
    op.drop_index("ix_section_entries_user_id", table_name="section_entries")
    op.drop_table("section_entries")

    op.drop_index("uq_active_group_members", table_name="group_members")
    op.drop_index("ix_group_members_user_id", table_name="group_members")
    op.drop_index("ix_group_members_group_id", table_name="group_members")
    op.drop_table("group_members")

    op.drop_table("groups")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_table("roles")

    # Drop enums last
    backup_status_enum = sa.Enum("success", "failed", name="backup_status")
    notification_type_enum = sa.Enum(
        "incomplete_day", "streak_milestone", "admin_action", "moderation", name="notification_type"
    )
    section_type_enum = sa.Enum("Health", "Happiness", "Hela", name="section_type")

    backup_status_enum.drop(op.get_bind(), checkfirst=True)
    notification_type_enum.drop(op.get_bind(), checkfirst=True)
    section_type_enum.drop(op.get_bind(), checkfirst=True)
