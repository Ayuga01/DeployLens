# DeployLens API

DeployLens is a minimal FastAPI service foundation with liveness and normalized
event ingestion endpoints. Events are stored in memory for now.

## Requirements

- Python 3.11.2
- [uv](https://docs.astral.sh/uv/) 0.13.0 or compatible

The pinned Python version is recorded in `.python-version`. `uv` creates the
project-local virtual environment in `.venv` and installs the exact locked
versions from `uv.lock`.

## Setup

```bash
uv sync --locked
```

To configure local environment values, copy `.env.example` to `.env`. The
health endpoint does not require environment variables or secrets.

## Run

```bash
uv run --locked uvicorn app.main:app --reload
```

The service is available at <http://127.0.0.1:8000>. Check it with:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok","service":"deploylens-api"}
```

Ingest an event and read it back by its `event_id`:

```bash
curl -i -X POST http://127.0.0.1:8000/events \
  -H 'Content-Type: application/json' \
  -d '{
    "event_id": "evt-123",
    "source": "github-actions",
    "event_type": "deployment",
    "service": "checkout",
    "timestamp": "2025-01-01T12:00:00Z",
    "severity": "info",
    "message": "Deployment completed",
    "metadata": {"environment": "production"}
  }'

curl http://127.0.0.1:8000/events/evt-123
```

The first submission returns `201 Created`, an identical retry returns `200 OK`,
and reusing an `event_id` with a different payload returns `409 Conflict`.

The equivalent Make target is `make run` (without reload).

## Test

Run the offline test suite with:

```bash
uv run --locked pytest
```

or:

```bash
make test
```

The test uses FastAPI's `TestClient` and does not start a server or require a
database.

## Deploy with Docker

Docker support is included for environments that provide Docker:

```bash
docker build -t deploylens-api .
docker run --rm -p 8000:8000 deploylens-api
```

`docker-compose.yml` documents a local Postgres 16 service for future API
work. Start it with `docker compose up postgres` when Docker is available; it
is not required by the current health endpoint.

## Project layout

- `app/main.py` — FastAPI application, health route, and in-memory event repository
- `tests/test_health.py` / `tests/test_events.py` — offline endpoint tests
- `pyproject.toml` / `uv.lock` — project metadata and locked dependencies
- `Dockerfile` / `docker-compose.yml` — container and local database setup
