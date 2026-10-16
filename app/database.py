"""Database engine and SQLAlchemy session configuration."""

from collections.abc import Iterator
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


DEFAULT_DATABASE_URL = "sqlite:///./deploylens.db"


def database_url() -> str:
    """Return the configured database URL, using the offline-friendly default."""

    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def create_db_engine(url: str | None = None) -> Engine:
    """Create an engine, using a thread-safe pool for in-memory SQLite tests."""

    resolved_url = url or database_url()
    engine_options: dict[str, object] = {}
    if resolved_url.startswith("sqlite"):
        engine_options["connect_args"] = {"check_same_thread": False}
        if resolved_url in {"sqlite://", "sqlite:///:memory:"}:
            engine_options["poolclass"] = StaticPool
    return create_engine(resolved_url, **engine_options)


def session_factory(engine: Engine) -> sessionmaker[Session]:
    """Build a non-expiring session factory for request and repository scopes."""

    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


engine = create_db_engine()
SessionLocal = session_factory(engine)


def get_session() -> Iterator[Session]:
    """Yield one database session for a request."""

    with SessionLocal() as session:
        yield session
