FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock README.md alembic.ini ./
COPY app ./app
COPY alembic ./alembic

RUN uv sync --locked --no-dev

EXPOSE 8000

CMD ["sh", "-c", "uv run --locked --no-dev alembic upgrade head && exec uv run --locked --no-dev uvicorn app.main:app --host 0.0.0.0 --port 8000"]
