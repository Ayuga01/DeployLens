# BUG-002: API port collision on local run

## Goal

Allow the local API smoke test to start when another process already owns the
default host port.

## Symptom

PostgreSQL started and the Alembic migration succeeded on host port `55432`, but
`make run` failed with:

```text
ERROR: [Errno 48] error while attempting to bind on address ('0.0.0.0', 8000): address already in use
make: *** [run] Error 1
```

## Evidence and root cause

- The database container was healthy enough for `alembic upgrade head` to reach
  PostgreSQL successfully.
- The failure occurred when Uvicorn tried to bind the API's fixed host port
  `8000`.
- A different local process, likely an earlier API instance or another service,
  already owned port `8000`.

## Fix

- `Makefile` now accepts `HOST` and `PORT` variables, defaulting to
  `0.0.0.0` and `8000`.
- README documents a collision recovery path using `PORT=8001`.
- No application behavior or dependency changed.

## Mac verification

Inspect the process using the default port if needed:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
```

Either stop that process, or run the API on another port:

```bash
PORT=8001 \
DATABASE_URL=postgresql+psycopg://deploylens:deploylens@localhost:55432/deploylens \
make run
```

In another terminal:

```bash
curl http://127.0.0.1:8001/health
```

Expected response:

```json
{"status":"ok","service":"deploylens-api"}
```

## Remaining gaps

- The project does not yet have a process supervisor or automatic port
  discovery. The developer must choose a free port.
- Authentication, rate limiting, and readiness checks remain future work.
