# ROLLBACK

## Code rollback

Last known good commit before this milestone:

```text
6a41c6b feat(events): add normalized event ingestion
```

If the persistence change fails review or local verification, return to that commit with a normal revert or branch reset workflow. Do not rewrite shared history.

## Schema rollback

The migration has a `downgrade()` that drops the `events` table and its indexes. Do not run it against a database containing data without first deciding how that data is backed up or discarded. For a disposable local database, use:

```bash
uv run --locked alembic downgrade base
```

Before a real deployment, take a PostgreSQL backup and test restoring it in a separate database.
