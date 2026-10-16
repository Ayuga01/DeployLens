# DECISIONS

## D-001: Use FastAPI for the API layer

Date: 2026-10-16  Model: omnirush/gpt-6-astra

Context: DeployLens needs a typed HTTP API that is easy to test and deploy.

Options: FastAPI, Flask, Django REST Framework.

Chosen: FastAPI.

Why: Pydantic validation, generated OpenAPI documentation, and a small async-capable surface fit this API better than a larger framework. Flask would require more validation and schema plumbing; Django would add more framework than the first slice needs.

Trade-off: We own more application structure than we would get from Django's conventions.

Revisit if: The project grows into a large admin-heavy product with substantial built-in identity and workflow requirements.

## D-002: Use SQLAlchemy plus Alembic for event persistence

Date: 2026-10-16  Model: omnirush/gpt-6-astra

Context: Events must survive API restarts and use a migration-controlled schema.

Options: SQLAlchemy + Alembic, a direct psycopg data-access layer, or a document database.

Chosen: SQLAlchemy 2.x with Alembic and PostgreSQL as the deployment database.

Why: The relational event shape has stable fields, the API needs lookup by `event_id` and filtering by service/time, and PostgreSQL gives durable transactions, indexes, and JSON metadata without introducing another datastore. Alembic makes schema changes reviewable and reversible.

Trade-off: ORM and migration setup add moving parts compared with direct SQL. The first local fallback uses SQLite, so PostgreSQL-specific behavior still needs a Docker smoke test.

Revisit if: Event volume or query patterns require a dedicated append-only/event-streaming store.

## D-003: Keep SQLite as the offline development default

Date: 2026-10-16  Model: omnirush/gpt-6-astra

Context: The project must have an offline `make test` command and the current worker does not provide Docker.

Options: Require PostgreSQL for every command, use SQLite for tests and PostgreSQL for deployment, or use a hosted database.

Chosen: SQLite for local default and isolated tests; PostgreSQL via `DATABASE_URL` for Docker and deployment.

Why: Contributors can run the core API and tests without a service dependency, while the application keeps a real PostgreSQL path and migration. Tests use temporary databases rather than a developer database.

Trade-off: SQLite is not identical to PostgreSQL for concurrency, JSON behavior, and timestamp storage.

Revisit if: PostgreSQL-specific behavior becomes part of the acceptance criteria for a feature.

## D-004: Map the Compose PostgreSQL service to a configurable host port

Date: 2026-10-16  Model: omnirush/gpt-6-astra

Context: The Mac setup path failed because host port `5432` was already in use,
while the PostgreSQL container still needs its standard internal port `5432`.

Options: Keep a fixed host port `5432`, use a configurable host port with a
collision-safer default, or assign a random host port.

Chosen: Use `POSTGRES_HOST_PORT` for the host mapping, defaulting to `5433`,
while retaining container port `5432`.

Why: Port `5433` avoids the common local PostgreSQL binding by default, and an
explicit environment variable lets a developer choose another free port without
changing the Compose file or application behavior. The README and example
environment keep the database URL aligned with the default.

Trade-off: Developers must use the mapped host port in `DATABASE_URL`, and
`5433` can still be occupied on an individual machine.

Revisit if: The project needs a standard host port for a shared local workflow
or a dynamically assigned port becomes preferable.

## D-005: Pin the Python 3.11 minor line instead of an unavailable patch

Date: 2026-10-16  Model: omnirush/gpt-6-astra

Context: The Mac ARM setup reported `No download found for request:
cpython-3.11.2-macos-aarch64-none` for `uv python install 3.11.2`, and the
following `uv sync` could not find Python 3.11.2. uv's managed Python downloads
are frozen per uv release.

Options: Keep the exact `3.11.2` pin, pin the `3.11` minor line, or rely on an
unmanaged system Python.

Chosen: Pin `.python-version` to `3.11`, install it with `uv python install
3.11`, and retain `pyproject.toml`'s `>=3.11,<3.12` requirement.

Why: The minor-line request lets uv select an available 3.11.x patch on the
target platform while preserving the project's supported runtime range. It
fixes the documented Mac ARM bootstrap failure without changing application
code, dependencies, or the lockfile.

Trade-off: The selected patch is resolved by uv/system and can vary as uv
download availability changes. Record the actual `Python 3.11.x` output from
`uv run --locked python --version` in `docs/HANDOVER.md` after setup.

Revisit if: The project requires byte-for-byte interpreter reproducibility or a
specific 3.11.x patch becomes available and supportable on every target.
