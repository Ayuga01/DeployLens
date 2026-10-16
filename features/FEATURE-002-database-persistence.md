# FEATURE-002: Database persistence

## Goal

Replace the process-local event dictionary with durable SQLAlchemy persistence while preserving the existing event API.

## Scope

- SQLAlchemy 2.x repository and ORM model.
- Alembic initial migration for the `events` table.
- PostgreSQL connection support through `DATABASE_URL`.
- SQLite fallback and isolated tests for offline development.
- No authentication, tenant isolation, queues, or automatic remediation.

## Acceptance criteria

- A new event survives a repository/session boundary.
- An identical retry returns `200`.
- A conflicting event ID returns `409` without overwriting the original row.
- Unknown IDs return `404`.
- `make test` passes without Docker or PostgreSQL.
- The schema can be created and downgraded through Alembic.

## Verification log

### 2026-10-16 — implementation

- Implemented SQLAlchemy engine/session configuration, ORM model, repository, and app factory.
- Added Alembic migration and PostgreSQL driver.
- Added isolated SQLite tests and migration checks.
- Reviewed the full diff and committed as `888b260`.
- Pending: verify the PostgreSQL/Docker Desktop path on the Mac.

## Open questions

- What authentication and tenant model should protect the future public ingestion endpoint?
- Should high-volume telemetry move to a separate append-only or streaming store?
