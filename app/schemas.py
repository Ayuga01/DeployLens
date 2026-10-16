"""Pydantic schemas for the public DeployLens API."""

from datetime import datetime
from typing import Annotated, Any, Literal

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
