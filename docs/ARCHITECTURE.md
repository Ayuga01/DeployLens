# ARCHITECTURE

## Current system

DeployLens is currently a single FastAPI process with a relational persistence boundary.

```text
HTTP client
    |
    v
FastAPI routes (app/main.py)
    |
    v
Pydantic Event schema (app/schemas.py)
    |
    v
SQLAlchemy repository (app/repository.py)
    |
    v
SQLAlchemy Session -> SQLite locally / PostgreSQL in Docker
    |
    v
events table (Alembic-managed)
```

## Trust boundaries

- External JSON enters at `POST /events` and is validated by Pydantic.
- The repository writes only validated `Event` values.
- Database credentials come from `DATABASE_URL`; they must not be committed.
- The current API is unauthenticated and is therefore a development/portfolio service, not a public production service.

## Ownership

- `app/main.py`: HTTP status codes, dependency wiring, and route behavior.
- `app/schemas.py`: public input/output contract.
- `app/models.py`: database table mapping and timestamp conversion.
- `app/repository.py`: persistence operations and ORM-to-schema conversion.
- `alembic/`: versioned schema changes.
