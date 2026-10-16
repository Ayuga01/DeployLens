"""SQLAlchemy ORM models used by DeployLens."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator


class Base(DeclarativeBase):
    """Base metadata for application models and Alembic."""


class AwareDateTime(TypeDecorator[datetime]):
    """Preserve offsets in SQLite and use timestamptz semantics in PostgreSQL."""

    impl = DateTime
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(DateTime(timezone=True))
        return dialect.type_descriptor(String(64))

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> str | datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include timezone information")
        if dialect.name == "sqlite":
            return value.isoformat()
        return value

    def process_result_value(self, value: str | datetime | None, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class EventModel(Base):
    """Persisted normalized event."""

    __tablename__ = "events"

    event_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    service: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(AwareDateTime(), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    event_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON, nullable=False, default=dict
    )
