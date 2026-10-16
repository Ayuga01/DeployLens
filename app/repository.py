"""Persistence operations for normalized events."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EventModel
from app.schemas import Event


def get_event(session: Session, event_id: str) -> EventModel | None:
    """Find an event by its unique public identifier."""

    return session.scalar(select(EventModel).where(EventModel.event_id == event_id))


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
