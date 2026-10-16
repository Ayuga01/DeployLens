"""FastAPI application entrypoint for DeployLens."""

from datetime import datetime
from typing import Annotated, Any, Literal

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field, StringConstraints, field_validator


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
EventType = Literal[
    "deployment",
    "log",
    "metric",
    "trace",
    "alert",
    "kubernetes_event",
]
Severity = Literal["debug", "info", "warning", "error", "critical"]


class Event(BaseModel):
    """A normalized event accepted by the ingestion API."""

    event_id: NonEmptyString
    source: NonEmptyString
    event_type: EventType
    service: NonEmptyString
    timestamp: datetime
    severity: Severity
    message: NonEmptyString
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_timezone_aware(cls, value: datetime) -> datetime:
        """Reject timestamps that do not identify a timezone or UTC offset."""

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include timezone information")
        return value


# This repository is intentionally in-memory until persistent storage is added.
events: dict[str, Event] = {}

app = FastAPI(title="DeployLens API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Return the service liveness status."""

    return {"status": "ok", "service": "deploylens-api"}


@app.post("/events", response_model=Event, status_code=status.HTTP_201_CREATED)
def ingest_event(event: Event, response: Response) -> Event:
    """Store an event, applying idempotency by event ID."""

    existing = events.get(event.event_id)
    if existing is None:
        events[event.event_id] = event
        return event

    if existing == event:
        response.status_code = status.HTTP_200_OK
        return existing

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="event_id already exists with a different payload",
    )


@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: str) -> Event:
    """Read a previously ingested event by ID."""

    event = events.get(event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="event not found")
    return event
