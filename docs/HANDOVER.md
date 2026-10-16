# HANDOVER

## Latest session: 2026-10-16 (model: omnirush/gpt-6-astra)

Done:
- Added `GET /incidents/correlate` for deterministic service/time-window
  summaries over persisted events.
- Added SQL filtering with inclusive bounds, chronological plus event-ID
  ordering, counts, latest deployment selection, and clear 422 validation.
- Added isolated SQLite tests and updated architecture, flow, data, decision,
  and feature records.
- Initialized the DeployLens FastAPI project with Python 3.11, uv.lock, Dockerfile,
  Compose, and offline tests.
- Added normalized event ingestion with idempotency and conflict handling.
- Replaced the in-memory event store with SQLAlchemy persistence and an Alembic
  migration.
- Recorded BUG-001 and BUG-002 and made the local PostgreSQL and API ports
  configurable.
- Committed the deterministic correlation milestone as `081d63e`; it is not
  pushed until the Mac PostgreSQL smoke path is verified.

In progress:
- Verify the correlation endpoint against the Mac's running PostgreSQL API.
- Push the incident-correlation milestone after Mac verification.

Broken or risky:
- Docker is unavailable in the current worker, so PostgreSQL behavior remains
  pending the existing Mac/Docker verification path.
- The API still has no authentication, rate limiting, or tenant isolation.
- Correlation is deterministic and rule-based; it does not infer causal
  relationships or use an LLM yet.

Next:
- On the Mac, use the running PostgreSQL API and call `/incidents/correlate` with
  `PORT=8001` and the database host port currently in use.
- Push commit `081d63e` after the correlation smoke test succeeds.

Do not touch:
- Do not commit `.env`, database files, `.opencode/` attachments, or
  credentials.
- Do not add automatic remediation, authentication, queues, LLMs, or schema
  migrations to this milestone.

Read first: `docs/ARCHITECTURE.md`, `docs/CONSTRAINTS.md`, `docs/DECISIONS.md`.
