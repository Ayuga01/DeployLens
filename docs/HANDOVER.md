# HANDOVER

## Latest session: 2026-10-16 (model: omnirush/gpt-6-astra)

Done:
- Initialized the DeployLens FastAPI project with Python 3.11, uv.lock, Dockerfile, Compose, and offline tests.
- Added normalized event ingestion with idempotency and conflict handling.
- Replaced the in-memory event store with SQLAlchemy persistence and an Alembic migration.
- Added an offline SQLite test path and PostgreSQL configuration for Docker development.
- Recorded BUG-001 and prepared the local setup repair: configurable Compose host port with a `5433` default, pinned-runtime installation instructions, and stale `.venv` recovery steps.
- Committed the setup repair as `1dbf0cc`, `90e4279`, `737a4d0`, `c97f761`, and `ab5a784`; these are now present on `origin/master`.
- Updated BUG-001 for the Mac ARM `3.11.2` download failure: `.python-version` now pins the `3.11` minor line, and the clean recovery path uses `uv python install 3.11`.
- Committed the Python bootstrap repair as `c97f761`; it is included in the pushed setup history.
- PostgreSQL started on host port `55432` and the migration succeeded on the Mac; the API then exposed BUG-002 because host port `8000` was already occupied.

In progress:
- Verify the local setup repair on the Mac with Docker Desktop and the pinned uv runtime.
- Add the first deterministic incident-correlation flow after persistence is stable.

Broken or risky:
- The Mac setup reported a Compose bind failure on host port `5432`, a stale `.venv` pointing to a missing interpreter, and `No download found for request: cpython-3.11.2-macos-aarch64-none`; the repair is unverified on the Mac.
- The selected Python patch is resolved by uv from the available 3.11 downloads rather than pinned exactly; record the actual `Python 3.11.x` from the version check below after Mac verification.
- Docker is unavailable in the current worker, so the PostgreSQL container and Docker image have not been run here.
- The default local database is SQLite; PostgreSQL behavior must be smoke-tested on the Mac with Docker Desktop.
- The API has no authentication, rate limiting, or tenant isolation yet. Do not treat it as production-ready.
- The default API port `8000` may be occupied by another local process; use `PORT=8001 make run` or inspect it with `lsof`.

Next:
- On the Mac, run `uv python install 3.11`, remove `.venv` if `.venv/bin/python --version` fails, then run `uv sync --locked` and `uv run --locked python --version` (expect `Python 3.11.x`). If uv reports no available download, run `brew update && brew upgrade uv` when uv came from Homebrew and retry.
- Record the selected `Python 3.11.x` patch from that version check in this handover.
- Verify `docker compose config`, `docker compose up -d postgres`, the migration, API, and curl flow using host port `5433`; set `POSTGRES_HOST_PORT` and mirror it in `DATABASE_URL` if `5433` is occupied.
- For the current Mac setup, the database is on host port `55432`; start the API with `PORT=8001` if `8000` is occupied and curl the matching port.
- Push the BUG-002 API port configurability fix after local review and Mac verification.
- Start incident correlation only after the persistence milestone is available remotely.

Do not touch:
- Do not commit `.env`, database files, `.opencode/` attachments, or credentials.
- Do not add automatic remediation, production credentials, or auth changes in the persistence milestone.

Read first: `docs/ARCHITECTURE.md`, `docs/CONSTRAINTS.md`, `docs/DECISIONS.md`.
