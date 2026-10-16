# CONSTRAINTS

- Always run `make test` after a code change.
- Keep the runtime pinned to the Python 3.11 minor line in `.python-version`,
  keep `pyproject.toml` at `>=3.11,<3.12`, and keep dependencies locked in
  `uv.lock`.
- Do not commit secrets, `.env`, database files, or `.opencode/` attachments.
- Do not bypass Pydantic validation at an HTTP boundary.
- Do not write to the database outside the repository layer.
- Database schema changes must use Alembic migrations.
- Do not add automatic remediation, shell execution, production credentials, or auth bypasses without a separate reviewed feature.
- Keep tests offline and isolated from a developer database.
- Read the full diff before committing AI-assisted changes.
