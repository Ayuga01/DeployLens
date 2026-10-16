# ASSUMPTIONS AND OPEN QUESTIONS

| Item | Status | Evidence or next check |
|---|---|---|
| The uv-managed Python 3.11 minor line works on the target Mac | Unverified here | Run `uv python install 3.11`, `uv sync --locked`, and record the `Python 3.11.x` output from `uv run --locked python --version` on the M1 Mac |
| PostgreSQL 16 Compose service works on Apple Silicon | Unverified here | Run `docker compose up -d postgres` on Docker Desktop |
| SQLite timestamp conversion matches PostgreSQL enough for current tests | Verified for current test cases | Add PostgreSQL integration tests before production claims |
| Event IDs are globally unique for the first API | Assumed | Revisit when multi-tenancy is added |
| Unauthenticated API is acceptable for local development only | Verified by constraint | Add auth before any public write endpoint |
