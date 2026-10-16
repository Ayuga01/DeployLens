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
