.PHONY: install migrate test run

HOST ?= 0.0.0.0
PORT ?= 8000

install:
	uv sync --locked

migrate:
	uv run --locked alembic upgrade head

test:
	uv run --locked pytest

run:
	uv run --locked uvicorn app.main:app --host $(HOST) --port $(PORT)
