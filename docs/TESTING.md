# TESTING

## Automated checks

Run from the repository root:

```bash
uv lock --check
uv sync --locked
make test
git diff --check
```

Expected result: all tests pass; `make test` must not need Docker, PostgreSQL, an API key, or a developer database.

## Manual customer path for the current milestone

1. Apply the schema with `make migrate`.
2. Start the API with `make run`.
3. Submit an event using the README `curl` example.
4. If port `8000` is occupied, start the API with `PORT=8001 make run` and use port `8001` for the remaining curl commands.
5. Submit the same event again and verify `200`.
6. Change the message and verify `409`.
7. Read the event back with `GET /events/{event_id}`.

## Known gap

The current worker has no Docker executable, so the PostgreSQL Compose path and Docker image are not verified here. They must be run on the Mac with Docker Desktop before claiming PostgreSQL deployment readiness.
