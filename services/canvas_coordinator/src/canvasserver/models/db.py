import logging
import os
from functools import lru_cache

import sqlalchemy
from sqlalchemy import inspect
from sqlalchemy.engine.base import Engine
from sqlmodel import Session, create_engine

from ..config import get_settings
from .db_models import Model

logger = logging.getLogger(__name__)


@lru_cache
def get_engine(get_settings=get_settings):
    settings = get_settings()
    sqlite_url = f"sqlite:///{settings.database_path}"
    connect_args = dict(check_same_thread=False)
    engine = create_engine(sqlite_url, connect_args=connect_args)
    return engine


def create_db_and_tables(engine: Engine | None):
    if engine is None:
        engine = get_engine()
    Model.metadata.create_all(engine)
    _create_triggers(engine)


def _create_triggers(engine: Engine):
    """
    DB-level trigger: delete a prompt automatically when its last image is removed.
    This enforces the invariant that prompts with no images are cleaned up immediately,
    regardless of how the image deletion occurs.
    """
    with engine.connect() as conn:
        conn.execute(
            sqlalchemy.text(
                """
                CREATE TRIGGER IF NOT EXISTS delete_prompt_when_empty
                AFTER DELETE ON image
                FOR EACH ROW
                WHEN (SELECT COUNT(*) FROM image WHERE prompt = OLD.prompt) = 0
                BEGIN
                    DELETE FROM frame_group_prompt WHERE prompt_id = OLD.prompt;
                    DELETE FROM prompt WHERE id = OLD.prompt;
                END
            """
            )
        )
        conn.commit()


def get_session():
    engine = get_engine()
    with Session(engine) as session:
        return session


def has_tables(engine):

    inspector = inspect(engine)
    schemas = inspector.get_schema_names()

    for schema in schemas:
        for table_name in inspector.get_table_names(schema=schema):
            logger.info(f"Found table '{table_name}', returning...")
            return True

    return False


def get_db_size(session):
    """Get sqlite database size in MB"""
    db_path = session.bind.url.database
    file_size_bytes = os.path.getsize(db_path)
    file_size_mb = file_size_bytes / (1024 * 1024)
    return file_size_mb
