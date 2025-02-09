import logging
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    app_name: str = "CanvasServer"
    database_path: Path = Path("./database.sqlite3")


@lru_cache
def get_settings():
    s = Settings()
    logger.info(f"config: {s}")
    return s
