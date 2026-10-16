# HANDOVER

## Latest session: 2026-10-16 (model: omnirush/gpt-6-astra)

Done:
- Initialized the DeployLens FastAPI project with Python 3.11.2, uv.lock, Dockerfile, Compose, and offline tests.
- Added normalized event ingestion with idempotency and conflict handling.
- Replaced the in-memory event store with SQLAlchemy persistence and an Alembic migration.
- Added an offline SQLite test path and PostgreSQL configuration for Docker development.
- Recorded BUG-001 and prepared the local setup repair: configurable Compose host port with a `5433` default, pinned-runtime installation instructions, and stale `.venv` recovery steps.
- Committed the setup repair locally as `1dbf0cc` plus the documentation correction as `90e4279`; neither is pushed until the Mac smoke path is verified.

In progress:
- Verify the local setup repair on the Mac with Docker Desktop and the pinned uv runtime.
- Add the first deterministic incident-correlation flow after persistence is stable.

Broken or risky:
- The Mac setup reported a Compose bind failure on host port `5432` and a stale `.venv` pointing to a missing interpreter; the repair is unverified on the Mac.
- Docker is unavailable in the current worker, so the PostgreSQL container and Docker image have not been run here.
- The default local database is SQLite; PostgreSQL behavior must be smoke-tested on the Mac with Docker Desktop.
- The API has no authentication, rate limiting, or tenant isolation yet. Do not treat it as production-ready.

Next:
- On the Mac, run `uv python install 3.11.2`, remove `.venv` if `.venv/bin/python --version` fails, then run `uv sync --locked`.
- Verify `docker compose config`, `docker compose up -d postgres`, the migration, API, and curl flow using host port `5433`; set `POSTGRES_HOST_PORT` and mirror it in `DATABASE_URL` if `5433` is occupied.
- Push the local setup-fix commits after the Mac verification succeeds: `1dbf0cc` and `90e4279`.
- Start incident correlation only after the persistence milestone is available remotely.

Do not touch:
- Do not commit `.env`, database files, `.opencode/` attachments, or credentials.
- Do not add automatic remediation, production credentials, or auth changes in the persistence milestone.

Read first: `docs/ARCHITECTURE.md`, `docs/CONSTRAINTS.md`, `docs/DECISIONS.md`.
