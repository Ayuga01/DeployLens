"""FastAPI application entrypoint for DeployLens."""

from collections.abc import Iterator
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from pydantic import ValidationError
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import create_db_engine, get_session, session_factory
from app.correlation import correlate_events
from app.repository import add_event, get_event, get_events_for_correlation, to_event
from app.schemas import CorrelationQuery, Event, IncidentCorrelation


def create_app(*, database_url: str | None = None, engine: Engine | None = None) -> FastAPI:
    """Create an application using an injectable SQLAlchemy engine."""

    application = FastAPI(title="DeployLens API", version="0.1.0")
    app_engine = engine or create_db_engine(database_url)
    app_session_factory = session_factory(app_engine)

    def session_dependency() -> Iterator[Session]:
        with app_session_factory() as session:
            yield session

    def correlation_query(
        service: str = Query(...),
        start_time: datetime = Query(...),
        end_time: datetime = Query(...),
    ) -> CorrelationQuery:
        """Turn query parameters into the shared schema and expose clear 422 errors."""

        try:
            return CorrelationQuery(
                service=service,
                start_time=start_time,
                end_time=end_time,
            )
        except ValidationError as exc:
            detail = "; ".join(error["msg"] for error in exc.errors())
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=detail,
            ) from exc

    application.dependency_overrides[get_session] = session_dependency

    @application.get("/health")
    def health() -> dict[str, str]:
        """Return the service liveness status."""

        return {"status": "ok", "service": "deploylens-api"}

    @application.post("/events", response_model=Event, status_code=status.HTTP_201_CREATED)
    def ingest_event(
        event: Event,
        response: Response,
        session: Session = Depends(get_session),
    ) -> Event:
        """Store an event, applying idempotency by event ID."""

        existing = get_event(session, event.event_id)
        if existing is not None:
            existing_event = to_event(existing)
            if existing_event == event:
                response.status_code = status.HTTP_200_OK
                return existing_event
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="event_id already exists with a different payload",
            )

        try:
            return to_event(add_event(session, event))
        except IntegrityError:
            # Another request may have inserted the same ID after the first read.
            concurrent = get_event(session, event.event_id)
            if concurrent is not None and to_event(concurrent) == event:
                response.status_code = status.HTTP_200_OK
                return to_event(concurrent)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="event_id already exists with a different payload",
            ) from None

    @application.get("/events/{event_id}", response_model=Event)
    def read_event(event_id: str, session: Session = Depends(get_session)) -> Event:
        """Read a previously ingested event by ID."""

        persisted = get_event(session, event_id)
        if persisted is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="event not found")
        return to_event(persisted)

    @application.get("/incidents/correlate", response_model=IncidentCorrelation)
    def correlate_incident(
        query: CorrelationQuery = Depends(correlation_query),
        session: Session = Depends(get_session),
    ) -> IncidentCorrelation:
        """Return a deterministic summary of persisted events for a time window."""

        persisted_events = get_events_for_correlation(
            session,
            service=query.service,
            start_time=query.start_time,
            end_time=query.end_time,
        )
        return correlate_events(query, persisted_events)

    return application


app = create_app()

# Keep the schema available to callers that import Event from app.main.
__all__ = ["Event", "app", "create_app"]
