"""create events table

Revision ID: 0001_create_events
Revises:
Create Date: 2026-10-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_create_events"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("event_id", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("service", sa.String(length=255), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index("ix_events_service", "events", ["service"], unique=False)
    op.create_index("ix_events_timestamp", "events", ["timestamp"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_events_timestamp", table_name="events")
    op.drop_index("ix_events_service", table_name="events")
    op.drop_table("events")
