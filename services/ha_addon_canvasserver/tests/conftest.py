import logging
from pathlib import Path

import pytest
from canvasserver.config import Settings
from canvasserver.main import app
from canvasserver.models.db import create_db_and_tables, get_session
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


@pytest.fixture()
def tmp_client(tmp_path: Path):

    print(f"Create database in {tmp_path}")

    settings = Settings(database_path=tmp_path / "database.sqlite3")
    sqlite_url = f"sqlite:///{settings.database_path}"
    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_session():
        print("Get fake session")
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    print("Create session maker override")
    app.dependency_overrides[get_session] = override_get_session

    # Create database
    print("Create database content")
    create_db_and_tables(engine)

    print("Create Test Client")
    client = TestClient(app)
    return client
