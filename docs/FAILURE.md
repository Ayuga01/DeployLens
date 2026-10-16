# FAILURE

## Dependency failures

- Database unavailable: API requests that access events fail; health currently remains a liveness check and does not prove database readiness.
- Migration not applied: event routes fail because the `events` table is missing. Run `make migrate` before starting a fresh database.
- Concurrent duplicate event: the primary-key constraint prevents a second row; the route re-reads and returns `200` or `409`.

## First limits

- SQLite is for local/offline development only and is not the concurrency target.
- PostgreSQL connection limits and event table growth will be reached before the AI investigation layer is production-scale.
- Unbounded message and metadata sizes are not yet protected by API limits.

## Detection

For this milestone, use HTTP error logs and database logs. Future work must add structured request/error metrics, database latency metrics, and readiness checks.
