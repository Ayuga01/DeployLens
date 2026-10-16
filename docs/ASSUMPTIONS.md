# ASSUMPTIONS AND OPEN QUESTIONS

| Item | Status | Evidence or next check |
|---|---|---|
| Python 3.11.2 and uv work on the target Mac | Unverified here | Run `uv sync --locked` on the M1 Mac |
| PostgreSQL 16 Compose service works on Apple Silicon | Unverified here | Run `docker compose up -d postgres` on Docker Desktop |
| SQLite timestamp conversion matches PostgreSQL enough for current tests | Verified for current test cases | Add PostgreSQL integration tests before production claims |
| Event IDs are globally unique for the first API | Assumed | Revisit when multi-tenancy is added |
| Unauthenticated API is acceptable for local development only | Verified by constraint | Add auth before any public write endpoint |
