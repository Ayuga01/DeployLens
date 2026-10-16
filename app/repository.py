"""Persistence operations for normalized events."""

from datetime import datetime

from sqlalchemy import func, literal, select
from sqlalchemy.orm import Session

from app.models import EventModel
from app.schemas import Event


def get_event(session: Session, event_id: str) -> EventModel | None:
    """Find an event by its unique public identifier."""

    return session.scalar(select(EventModel).where(EventModel.event_id == event_id))


def get_events_for_correlation(
    session: Session,
    *,
    service: str,
    start_time: datetime,
    end_time: datetime,
) -> list[EventModel]:
    """Load one service's events inside an inclusive, deterministic time window."""

    if session.get_bind().dialect.name == "sqlite":
        # SQLite stores offsets as text through AwareDateTime. julianday makes
        # comparisons and ordering use the represented instant, not the text's
        # local-clock prefix, while keeping the filtering in SQL.
        timestamp_value = func.julianday(EventModel.timestamp)
        start_value = func.julianday(literal(start_time.isoformat()))
        end_value = func.julianday(literal(end_time.isoformat()))
    else:
        timestamp_value = EventModel.timestamp
        start_value = start_time
        end_value = end_time

    statement = (
        select(EventModel)
        .where(
            EventModel.service == service,
            timestamp_value >= start_value,
            timestamp_value <= end_value,
        )
        .order_by(timestamp_value.asc(), EventModel.event_id.asc())
    )
    return list(session.scalars(statement).all())


def add_event(session: Session, event: Event) -> EventModel:
    """Insert and commit an event, rolling back so callers can handle conflicts."""

    persisted = EventModel(
        event_id=event.event_id,
        source=event.source,
        event_type=event.event_type,
        service=event.service,
        timestamp=event.timestamp,
        severity=event.severity,
        message=event.message,
        event_metadata=event.metadata,
    )
    session.add(persisted)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
    session.refresh(persisted)
    return persisted


def to_event(model: EventModel) -> Event:
    """Convert a persisted row back to the public API schema."""

    return Event.model_validate(
        {
            "event_id": model.event_id,
            "source": model.source,
            "event_type": model.event_type,
            "service": model.service,
            "timestamp": model.timestamp,
            "severity": model.severity,
            "message": model.message,
            "metadata": model.event_metadata,
        }
    )
