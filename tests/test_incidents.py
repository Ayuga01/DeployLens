import pytest


def event_payload(event_id: str, **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "event_id": event_id,
        "source": "test-suite",
        "event_type": "log",
        "service": "checkout",
        "timestamp": "2025-01-01T12:00:00Z",
        "severity": "info",
        "message": f"event {event_id}",
    }
    payload.update(overrides)
    return payload


def ingest(client, *payloads: dict[str, object]) -> None:
    for payload in payloads:
        response = client.post("/events", json=payload)
        assert response.status_code == 201


def correlation_params(**overrides: str) -> dict[str, str]:
    params = {
        "service": "checkout",
        "start_time": "2025-01-01T12:00:00Z",
        "end_time": "2025-01-01T13:00:00Z",
    }
    params.update(overrides)
    return params


def test_correlation_includes_boundaries_and_orders_by_timestamp_then_id(client) -> None:
    ingest(
        client,
        event_payload("evt-z", timestamp="2025-01-01T12:30:00Z"),
        event_payload("evt-b", timestamp="2025-01-01T12:15:00Z"),
        event_payload("evt-a", timestamp="2025-01-01T12:15:00Z"),
        event_payload("evt-start", timestamp="2025-01-01T12:00:00Z"),
        event_payload("evt-end", timestamp="2025-01-01T13:00:00Z"),
        event_payload("evt-after", timestamp="2025-01-01T13:00:00.001Z"),
    )

    response = client.get("/incidents/correlate", params=correlation_params())

    assert response.status_code == 200
    body = response.json()
    assert body["event_count"] == 5
    assert [event["event_id"] for event in body["events"]] == [
        "evt-start",
        "evt-a",
        "evt-b",
        "evt-z",
        "evt-end",
    ]


def test_correlation_isolates_service_and_time_window(client) -> None:
    ingest(
        client,
        event_payload("checkout-in", timestamp="2025-01-01T12:30:00Z"),
        event_payload("checkout-before", timestamp="2025-01-01T11:59:59Z"),
        event_payload("checkout-after", timestamp="2025-01-01T13:00:01Z"),
        event_payload("payments-in", service="payments", timestamp="2025-01-01T12:30:00Z"),
    )

    response = client.get("/incidents/correlate", params=correlation_params())

    assert response.status_code == 200
    assert [event["event_id"] for event in response.json()["events"]] == ["checkout-in"]


def test_correlation_compares_timezone_offsets_as_instants(client) -> None:
    ingest(
        client,
        event_payload("evt-later", timestamp="2025-01-01T11:30:00+02:00"),
        event_payload("evt-earlier", timestamp="2025-01-01T09:29:00Z"),
    )

    response = client.get(
        "/incidents/correlate",
        params=correlation_params(
            start_time="2025-01-01T09:30:00Z",
            end_time="2025-01-01T09:30:00Z",
        ),
    )

    assert response.status_code == 200
    assert [event["event_id"] for event in response.json()["events"]] == ["evt-later"]


def test_correlation_returns_counts_and_latest_deployment(client) -> None:
    ingest(
        client,
        event_payload(
            "evt-deploy-old",
            event_type="deployment",
            severity="warning",
            timestamp="2025-01-01T12:10:00Z",
        ),
        event_payload(
            "evt-alert",
            event_type="alert",
            severity="error",
            timestamp="2025-01-01T12:20:00Z",
        ),
        event_payload(
            "evt-deploy-new",
            event_type="deployment",
            severity="info",
            timestamp="2025-01-01T12:30:00Z",
        ),
    )

    response = client.get("/incidents/correlate", params=correlation_params())

    assert response.status_code == 200
    body = response.json()
    assert body["counts_by_type"] == {"alert": 1, "deployment": 2}
    assert body["counts_by_severity"] == {"error": 1, "info": 1, "warning": 1}
    assert body["latest_deployment"]["event_id"] == "evt-deploy-new"


def test_correlation_returns_empty_result_for_unknown_service_or_window(client) -> None:
    response = client.get(
        "/incidents/correlate",
        params=correlation_params(
            service="unknown",
            start_time="2026-01-01T00:00:00Z",
            end_time="2026-01-01T01:00:00Z",
        ),
    )

    assert response.status_code == 200
    assert response.json() == {
        "service": "unknown",
        "start_time": "2026-01-01T00:00:00Z",
        "end_time": "2026-01-01T01:00:00Z",
        "event_count": 0,
        "events": [],
        "counts_by_type": {},
        "counts_by_severity": {},
        "latest_deployment": None,
    }


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"start_time": "2025-01-01T12:00:00"}, "timezone information"),
        (
            {"start_time": "2025-01-01T13:00:00Z", "end_time": "2025-01-01T12:00:00Z"},
            "end_time must be greater than or equal to start_time",
        ),
    ],
)
def test_correlation_rejects_invalid_time_ranges(
    client, overrides: dict[str, str], message: str
) -> None:
    response = client.get("/incidents/correlate", params=correlation_params(**overrides))

    assert response.status_code == 422
    assert message in response.text
