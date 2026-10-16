from datetime import datetime

from sqlalchemy.orm import Session

from app.database import session_factory
from app.models import EventModel
from app.repository import add_event, get_event, to_event
from app.schemas import Event


def event_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "event_id": "evt-123",
        "source": "github-actions",
        "event_type": "deployment",
        "service": "checkout",
        "timestamp": "2025-01-01T12:00:00Z",
        "severity": "info",
        "message": "Deployment completed",
    }
    payload.update(overrides)
    return payload


def test_create_and_read_back_event(client) -> None:
    create_response = client.post("/events", json=event_payload())

    assert create_response.status_code == 201
    assert create_response.json()["metadata"] == {}

    read_response = client.get("/events/evt-123")

    assert read_response.status_code == 200
    assert read_response.json() == create_response.json()


def test_invalid_event_type_returns_validation_error(client) -> None:
    response = client.post("/events", json=event_payload(event_type="incident"))

    assert response.status_code == 422
    assert any(error["loc"][-1] == "event_type" for error in response.json()["detail"])


def test_missing_timezone_returns_validation_error(client) -> None:
    response = client.post(
        "/events", json=event_payload(timestamp="2025-01-01T12:00:00")
    )

    assert response.status_code == 422
    assert any(
        error["loc"][-1] == "timestamp"
        and "timezone" in error["msg"]
        for error in response.json()["detail"]
    )


def test_identical_duplicate_returns_existing_event(client) -> None:
    payload = event_payload()

    first_response = client.post("/events", json=payload)
    duplicate_response = client.post("/events", json=payload)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 200
    assert duplicate_response.json() == first_response.json()


def test_conflicting_duplicate_returns_conflict(client) -> None:
    client.post("/events", json=event_payload())
    response = client.post("/events", json=event_payload(message="Deployment failed"))

    assert response.status_code == 409
    assert response.json() == {"detail": "event_id already exists with a different payload"}


def test_unknown_event_returns_not_found(client) -> None:
    response = client.get("/events/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"detail": "event not found"}


def test_event_persists_across_repository_session_boundaries(database) -> None:
    payload = Event(**event_payload(metadata={"environment": "production"}))
    sessions = session_factory(database)

    with sessions() as first_session:
        persisted = add_event(first_session, payload)
        assert persisted.event_id == payload.event_id

    with sessions() as second_session:
        loaded = get_event(second_session, payload.event_id)
        assert loaded is not None
        assert to_event(loaded) == payload
        assert loaded.timestamp == datetime.fromisoformat("2025-01-01T12:00:00+00:00")


def test_event_row_has_unique_primary_key(database) -> None:
    with Session(database) as session:
        columns = {column.name: column for column in EventModel.__table__.columns}
        assert columns["event_id"].primary_key
        assert columns["metadata"].nullable is False
