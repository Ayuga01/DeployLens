from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from app.database import create_db_engine
from app.main import create_app
from app.models import Base


@pytest.fixture
def database(tmp_path) -> Generator[Engine, None, None]:
    engine = create_db_engine(f"sqlite:///{tmp_path / 'events.db'}")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(database: Engine) -> Generator[TestClient, None, None]:
    with TestClient(create_app(engine=database)) as test_client:
        yield test_client
