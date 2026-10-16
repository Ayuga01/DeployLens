# ALTERNATIVES

## Persistence

### Chosen: PostgreSQL with SQLAlchemy and Alembic

Durable relational storage, transactions, indexes, and JSON metadata. It is easy to run in Docker and is widely understood by backend teams.

### Rejected: Direct psycopg SQL only

It would reduce ORM abstraction but require more manual mapping and migration/query plumbing for a project that will grow beyond one table.

### Rejected: Document database

Flexible event payloads are attractive, but the current access pattern already has stable fields and needs exact idempotency plus service/time indexes.

Revisit if: event volume or source-specific payloads make relational storage the bottleneck.
