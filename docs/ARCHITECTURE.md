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
Pydantic schemas (app/schemas.py)
    |
    +--> SQLAlchemy repository (app/repository.py)
    |        |
    |        v
    |    SQLAlchemy Session -> SQLite locally / PostgreSQL in Docker
    |        |
    |        v
    |    events table (Alembic-managed)
    |
    +--> deterministic correlation (app/correlation.py)
             |
             v
        IncidentCorrelation response
```

## Trust boundaries

- External JSON enters at `POST /events` and is validated by Pydantic.
- The repository writes only validated `Event` values.
- Database credentials come from `DATABASE_URL`; they must not be committed.
- The current API is unauthenticated and is therefore a development/portfolio service, not a public production service.

## Ownership

- `app/main.py`: HTTP status codes, dependency wiring, and route behavior.
- `app/schemas.py`: public event and correlation input/output contracts.
- `app/models.py`: database table mapping and timestamp conversion.
- `app/repository.py`: persistence operations, SQL filtering/order, and ORM-to-schema conversion.
- `app/correlation.py`: deterministic counts and latest-deployment selection over repository results.
- `alembic/`: versioned schema changes.

## Incident correlation boundary

`GET /incidents/correlate` validates the service and timezone-aware interval at the HTTP boundary, then asks the repository for exactly that service and inclusive timestamp window. SQL orders rows by timestamp and `event_id`; the correlation module only summarizes those rows. No AI model, external service, queue, or automatic remediation participates in this path.
