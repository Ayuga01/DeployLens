"""Pydantic schemas for the public DeployLens API."""

from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, StringConstraints, field_validator, model_validator


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


class CorrelationQuery(BaseModel):
    """Validated query parameters for deterministic incident correlation."""

    service: NonEmptyString
    start_time: datetime
    end_time: datetime

    @field_validator("start_time", "end_time")
    @classmethod
    def query_time_must_be_timezone_aware(cls, value: datetime) -> datetime:
        """Require an explicit timezone or UTC offset for every query boundary."""

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("datetime must include timezone information")
        return value

    @model_validator(mode="after")
    def end_time_must_not_precede_start_time(self) -> "CorrelationQuery":
        """Keep the requested interval ordered and therefore unambiguous."""

        if self.end_time < self.start_time:
            raise ValueError("end_time must be greater than or equal to start_time")
        return self


class IncidentCorrelation(BaseModel):
    """Explainable event summary for one service and inclusive time window."""

    service: str
    start_time: datetime
    end_time: datetime
    event_count: int
    events: list[Event]
    counts_by_type: dict[str, int]
    counts_by_severity: dict[str, int]
    latest_deployment: Event | None
