# FEATURE-003: Incident correlation

## Goal

Expose a deterministic, explainable summary of persisted events for one
service and an inclusive timezone-aware time window.

## Scope

- Add `GET /incidents/correlate?service=<non-empty>&start_time=<timezone-aware ISO datetime>&end_time=<timezone-aware ISO datetime>`.
- Filter persisted events by exact service and inclusive timestamp bounds.
- Return chronological events with `event_id` as the deterministic tie-breaker.
- Return event count, counts by type and severity, and the latest deployment.
- Keep the existing event endpoints, database schema, and dependency set unchanged.
- No authentication, LLMs, queues, migrations, or automatic remediation.

## Decisions

- Query filtering and ordering stay in the SQLAlchemy repository so the
  correlation input is bounded and auditable.
- `app/correlation.py` owns only the explainable summary calculations.
- Timestamps are validated as timezone-aware, and a reversed interval is a
  422 validation error.
- Empty valid queries are successful responses with empty collections and a
  null latest deployment.
- See D-007 in `docs/DECISIONS.md` for the alternatives and rationale.

## Implementation

- Added `CorrelationQuery` and `IncidentCorrelation` schemas.
- Added `get_events_for_correlation` with inclusive predicates and stable
  ordering.
- Added the `/incidents/correlate` route and isolated SQLite tests for the
  requested boundaries, isolation, summary, empty, and invalid cases.
- Added SQLite instant-aware ordering/filtering for persisted timestamps that
  carry different UTC offsets; PostgreSQL continues to use its native
  timezone-aware comparison.

## Verification log

### 2026-10-16 — implementation

- `uv lock --check` — passed (`Resolved 29 packages in 2ms`).
- `uv sync --locked` — passed (`Checked 27 packages in 11ms`).
- `make test` — passed, 16 tests.
- `git diff --check` — passed with no output.
- Coverage includes inclusive boundaries, chronological/tie ordering, service
  isolation, time-window exclusion, counts, latest deployment, empty results,
  offset-aware instant comparison, naive timestamps, and reversed windows.
- No schema migration was required because this feature reads the existing
  `events` table.

## Open questions

- Should future correlation support explicit causal relationships or remain a
  documented set of deterministic rules?
- What production query volume would justify a composite `(service,
  timestamp)` index in addition to the existing single-column indexes?
