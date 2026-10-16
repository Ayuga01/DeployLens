.PHONY: install migrate test run

install:
	uv sync --locked

migrate:
	uv run --locked alembic upgrade head

test:
	uv run --locked pytest

run:
	uv run --locked uvicorn app.main:app --host 0.0.0.0 --port 8000
