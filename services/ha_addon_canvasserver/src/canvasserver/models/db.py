from functools import lru_cache

from sqlmodel import Session, create_engine

from ..config import get_settings
from .content import Model


@lru_cache
def get_engine(get_settings=get_settings):
    settings = get_settings()
    sqlite_url = f"sqlite:///{settings.database_path}"
    print("url", sqlite_url)
    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, connect_args=connect_args)
    return engine


def create_db_and_tables(engine):
    if engine is None:
        engine = get_engine()
    Model.metadata.create_all(engine)


def get_session():
    print("Connects to wrong database!")
    engine = get_engine()
    with Session(engine) as session:
        return session
