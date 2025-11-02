import json
import logging
import os
from functools import lru_cache
from pathlib import Path

from canvasserver.constants import ENV_CONFIG_PATH, ENV_DATA_PATH, MAX_DISK_SIZE
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    app_name: str = "CanvasServer"
    database_path: Path = Path("./database.sqlite3")
    max_disk_size: int = MAX_DISK_SIZE

    log_level: str = "INFO"


# TODO Remove from query endpoints
# storage: str | None = Query(default=None, include_in_schema=False),
# config_path: str | None = Query(default=None, include_in_schema=False),


@lru_cache
def get_settings(
    # storage: Path | None = None,
    # config_path: Path | None = None,
):

    storage: Path | None = None
    config_path: Path | None = None

    here = Path("./")

    # Read environ stuff
    if storage is None:
        storage = Path(os.environ.get(ENV_DATA_PATH, here))

    if config_path is None:
        config_path = Path(os.environ.get(ENV_CONFIG_PATH, here / "options.json"))

    assert storage.is_dir(), "Storage directory is wrong"

    options = None
    if config_path is not None and Path(config_path).is_file():
        with open(config_path, "r") as f:
            options = json.load(f)

    logger.info(f"reading options: {options}")

    database_path = storage / "database.sqlite3"

    logger.info(f"Setting database to {database_path}")

    if options is None:
        options = dict(database_path=database_path)
    else:
        options["database_path"] = database_path

    settings = Settings(**options)
    logger.info(f"config: {settings}")
    return settings
