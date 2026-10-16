.PHONY: install test run

install:
	uv sync --locked

test:
	uv run --locked pytest

run:
	uv run --locked uvicorn app.main:app --host 0.0.0.0 --port 8000
