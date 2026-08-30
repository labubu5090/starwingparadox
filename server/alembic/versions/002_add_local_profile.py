"""Add local_profile table for operator-owned private profiles.

Revision ID: 002_local_profile
Revises: 001_initial
Create Date: 2026-08-30
"""

from alembic import op
import sqlalchemy as sa

revision = "002_local_profile"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "local_profile",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("profile_uuid", sa.String(36), unique=True, nullable=False),
        sa.Column("display_name", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tutorial_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tutorial_completed", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("tutorial_last_result", sa.String(32), nullable=True),
        sa.Column("preferred_controller_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("settings_json", sa.Text(), nullable=True),
        sa.Column("session_active", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("session_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_local_profile_profile_uuid", "local_profile", ["profile_uuid"], unique=True)
    op.create_index("ix_local_profile_session_active", "local_profile", ["session_active"])


def downgrade() -> None:
    op.drop_index("ix_local_profile_session_active", table_name="local_profile")
    op.drop_index("ix_local_profile_profile_uuid", table_name="local_profile")
    op.drop_table("local_profile")
