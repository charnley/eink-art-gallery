import logging
from functools import lru_cache

from sqlalchemy import inspect
from sqlalchemy.engine.base import Engine
from sqlmodel import Session, create_engine

from ..config import get_settings
from .content import Model

logger = logging.getLogger(__name__)


@lru_cache
def get_engine(get_settings=get_settings):
    settings = get_settings()
    sqlite_url = f"sqlite:///{settings.database_path}"
    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, connect_args=connect_args)
    return engine


def create_db_and_tables(engine: Engine | None):
    if engine is None:
        engine = get_engine()
    Model.metadata.create_all(engine)


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
