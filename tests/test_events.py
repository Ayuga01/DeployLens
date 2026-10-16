from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app, events


@pytest.fixture(autouse=True)
def clear_event_repository() -> Generator[None, None, None]:
    events.clear()
    yield
    events.clear()


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


def test_create_and_read_back_event() -> None:
    client = TestClient(app)

    create_response = client.post("/events", json=event_payload())

    assert create_response.status_code == 201
    assert create_response.json()["metadata"] == {}

    read_response = client.get("/events/evt-123")

    assert read_response.status_code == 200
    assert read_response.json() == create_response.json()


def test_invalid_event_type_returns_validation_error() -> None:
    response = TestClient(app).post("/events", json=event_payload(event_type="incident"))

    assert response.status_code == 422
    assert any(error["loc"][-1] == "event_type" for error in response.json()["detail"])


def test_missing_timezone_returns_validation_error() -> None:
    response = TestClient(app).post(
        "/events", json=event_payload(timestamp="2025-01-01T12:00:00")
    )

    assert response.status_code == 422
    assert any(
        error["loc"][-1] == "timestamp"
        and "timezone" in error["msg"]
        for error in response.json()["detail"]
    )


def test_identical_duplicate_returns_existing_event() -> None:
    client = TestClient(app)
    payload = event_payload()

    first_response = client.post("/events", json=payload)
    duplicate_response = client.post("/events", json=payload)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 200
    assert duplicate_response.json() == first_response.json()


def test_conflicting_duplicate_returns_conflict() -> None:
    client = TestClient(app)

    client.post("/events", json=event_payload())
    response = client.post("/events", json=event_payload(message="Deployment failed"))

    assert response.status_code == 409
    assert response.json() == {"detail": "event_id already exists with a different payload"}


def test_unknown_event_returns_not_found() -> None:
    response = TestClient(app).get("/events/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"detail": "event not found"}
