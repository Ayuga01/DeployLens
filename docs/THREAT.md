# THREAT

## Current actors and entry points

- Anonymous HTTP caller can submit arbitrary JSON to `POST /events`.
- A caller can replay an event or reuse an existing `event_id`.
- A caller can send oversized strings or metadata objects.
- A compromised dependency or database credential could read or alter stored events.

## Current mitigations

- Pydantic validates required fields, enums, and timezone-aware timestamps.
- `event_id` is a database primary key, and conflicting replays return `409` rather than overwriting data.
- SQLAlchemy parameterizes database operations.
- Secrets are supplied through environment configuration and ignored by Git.

## Known gaps

- No authentication, authorization, rate limiting, request-size limit, tenant isolation, or audit logging exists yet.
- The unauthenticated API must not be exposed to real customers or production data.
