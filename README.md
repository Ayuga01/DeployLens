# DeployLens API

DeployLens is a minimal FastAPI service foundation with liveness and normalized
event ingestion endpoints. Events are persisted with SQLAlchemy and Alembic.

## Requirements

- Python 3.11.2
- [uv](https://docs.astral.sh/uv/) 0.13.0 or compatible

The pinned Python version is recorded in `.python-version`. `uv` creates the
project-local virtual environment in `.venv` and installs the exact locked
versions from `uv.lock`.

## Setup

```bash
# Install the exact interpreter pinned by .python-version.
uv python install 3.11.2

# Recreate a stale project environment whose interpreter is missing.
if [ -d .venv ] && ! .venv/bin/python --version >/dev/null 2>&1; then
  rm -rf .venv
fi

uv sync --locked
```

The stale-environment check is safe to repeat: it removes `.venv` only when its
Python executable cannot run, and `uv sync --locked` recreates it. Keep
`.python-version` pinned to `3.11.2`.

To configure local environment values, copy `.env.example` to `.env`. The
default `DATABASE_URL` is `sqlite:///./deploylens.db`, so local development
does not require Docker or PostgreSQL. The PostgreSQL URL supported by the
included Compose service is:

```text
postgresql+psycopg://deploylens:deploylens@localhost:5433/deploylens
```

Compose keeps PostgreSQL on container port `5432` and maps host port `5433` by
default. Set `POSTGRES_HOST_PORT` to another free host port when needed, and
use the same port in `DATABASE_URL`.

Apply the schema before starting the API:

```bash
make migrate
```

`make migrate` reads `DATABASE_URL` from the environment and runs Alembic's
migrations. For example, to use PostgreSQL locally:

```bash
docker compose up -d postgres
DATABASE_URL=postgresql+psycopg://deploylens:deploylens@localhost:5433/deploylens make migrate
DATABASE_URL=postgresql+psycopg://deploylens:deploylens@localhost:5433/deploylens make run
```

To override the host port, keep the container port at `5432` and mirror the
override in the database URL. For example:

```bash
POSTGRES_HOST_PORT=55432 docker compose up -d postgres
DATABASE_URL=postgresql+psycopg://deploylens:deploylens@localhost:55432/deploylens make migrate
```

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

The offline test suite uses an isolated temporary SQLite database per test. It
does not require Docker, PostgreSQL, or a developer database.

## Deploy with Docker

Docker support is included for environments that provide Docker:

```bash
docker build -t deploylens-api .
docker run --rm -p 8000:8000 deploylens-api
```

`docker-compose.yml` provides a PostgreSQL 16 service with the development
credentials used in the URL above. Start it with `docker compose up -d
postgres` when Docker is available. Docker is only needed for PostgreSQL
development; SQLite remains the default for offline work.

## Project layout

- `app/main.py` — FastAPI application factory and API routes
- `app/database.py` — configurable SQLAlchemy engine and session dependency
- `app/models.py` / `app/repository.py` — ORM model and persistence operations
- `alembic/` / `alembic.ini` — database migration configuration and revisions
- `tests/` — isolated SQLite endpoint and persistence tests
- `pyproject.toml` / `uv.lock` — project metadata and locked dependencies
- `Dockerfile` / `docker-compose.yml` — container and local database setup
- `docs/` — architecture, flow, constraints, decisions, testing, threat, failure,
  rollback, and handover notes
- `features/` — scoped feature traces and verification logs

## Defend what you ship

This project follows the repository workflow in the attached *Defend What You
Ship* field guide. Before accepting an AI-assisted change, read the full diff,
record meaningful decisions and alternatives, run the exact test checklist, and
keep rollback and handover notes current. The current persistence milestone is
tracked in `features/FEATURE-002-database-persistence.md`.
