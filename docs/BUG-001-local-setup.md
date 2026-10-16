# BUG-001: Local setup failures on Mac

## Goal

Restore the documented local setup path without changing application behavior or
locked dependencies.

## Symptom

- `docker compose up -d postgres` failed because host port `5432` was already in
  use.
- `uv` failed during setup because the existing project `.venv` referenced a
  Python interpreter that was no longer present, and the pinned Python patch
  `3.11.2` was not available in the managed `uv` runtimes for the Mac ARM
  request.

## Evidence

- The original Compose mapping was the fixed binding `5432:5432`.
- Before this repair, `.python-version` pinned the project to the exact version
  `3.11.2`.
- The setup instructions ran `uv sync --locked` before installing that pinned
  runtime or checking whether `.venv/bin/python` could still execute.
- The user's Mac terminal reported:
  `uv python install 3.11.2` → `No download found for request:
  cpython-3.11.2-macos-aarch64-none`.
- The same machine then reported that `uv sync` could not find Python 3.11.2.
- The uv documentation explains that managed Python downloads are frozen per uv
  release and recommends installing an available minor line such as `3.11`.

## Root cause

Three machine-local assumptions were encoded in the setup path: host port
`5432` was assumed to be free, an existing `.venv` was assumed to remain valid
after its original interpreter disappeared, and an exact Python patch was
assumed to be available in the installed uv release. The Mac ARM download
request proved that `3.11.2` is not available there, so the exact patch pin
prevented uv from resolving the runtime.

## Fix

- Map Compose's host port through `POSTGRES_HOST_PORT`, defaulting to `5433`,
  while keeping the container on port `5432`.
- Add `POSTGRES_HOST_PORT=5433` and the matching PostgreSQL URL to
  `.env.example`.
- Update README commands and URLs to use `5433`, and document an override for a
  different free host port.
- Pin `.python-version` to the available Python `3.11` minor line and update
  setup instructions to run `uv python install 3.11`, remove `.venv` only when
  its Python executable cannot run, and then run `uv sync --locked`.
- Keep `pyproject.toml`'s `>=3.11,<3.12` requirement, `uv.lock`, application
  code, and dependencies unchanged.

If the minor-line install still reports that no download is available, update uv
when it came from Homebrew and retry:

```bash
brew update && brew upgrade uv
```

## Mac verification commands

Run these from the repository root on the Mac:

```bash
test "$(cat .python-version)" = "3.11"
uv python install 3.11

if [ -d .venv ] && ! .venv/bin/python --version >/dev/null 2>&1; then
  rm -rf .venv
fi

uv sync --locked
uv run --locked python --version  # expect Python 3.11.x
make test

docker compose config
docker compose up -d postgres
DATABASE_URL=postgresql+psycopg://deploylens:deploylens@localhost:5433/deploylens make migrate
```

In another terminal, start the API and exercise the health endpoint:

```bash
DATABASE_URL=postgresql+psycopg://deploylens:deploylens@localhost:5433/deploylens make run
curl http://127.0.0.1:8000/health
```

Expected health response:

```json
{"status":"ok","service":"deploylens-api"}
```

If `5433` is also occupied, choose a free port and use it consistently:

```bash
POSTGRES_HOST_PORT=55432 docker compose up -d postgres
DATABASE_URL=postgresql+psycopg://deploylens:deploylens@localhost:55432/deploylens make migrate
```

Clean up the Mac verification container when finished:

```bash
docker compose down
```

## Remaining gaps

- Docker Desktop and the PostgreSQL migration/API smoke path are unavailable in
  the current worker and therefore remain unverified here.
- A different local process can still occupy `5433`; the documented override is
  the recovery path.
- The Mac-specific `uv` runtime installation and stale-environment recovery still
  need to be run and confirmed on the user's machine. Record the selected
  `Python 3.11.x` from `uv run --locked python --version` in the handover.
