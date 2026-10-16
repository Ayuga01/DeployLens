"""Deterministic incident-correlation calculations over persisted events."""

from collections import Counter
from collections.abc import Sequence

from app.models import EventModel
from app.repository import to_event
from app.schemas import CorrelationQuery, IncidentCorrelation


def correlate_events(
    query: CorrelationQuery,
    persisted_events: Sequence[EventModel],
) -> IncidentCorrelation:
    """Summarize already-filtered events without inference or external services."""

    events = [to_event(event) for event in persisted_events]
    counts_by_type = dict(sorted(Counter(event.event_type for event in events).items()))
    counts_by_severity = dict(sorted(Counter(event.severity for event in events).items()))

    # The repository orders by timestamp and event ID, so the final matching
    # deployment is deterministic even when multiple events share a timestamp.
    deployments = [event for event in events if event.event_type == "deployment"]
    latest_deployment = deployments[-1] if deployments else None

    return IncidentCorrelation(
        service=query.service,
        start_time=query.start_time,
        end_time=query.end_time,
        event_count=len(events),
        events=events,
        counts_by_type=counts_by_type,
        counts_by_severity=counts_by_severity,
        latest_deployment=latest_deployment,
    )
