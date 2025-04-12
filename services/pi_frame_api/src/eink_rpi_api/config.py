import json
import logging
import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

from .constants import ENV_CONFIG_PATH
from .displaying import EpdType

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    log_level: str = "INFO"
    cron_refresh: str | None = None
    EPD_TYPE: EpdType


@lru_cache
def get_settings(config_path: Path | None = None):

    here = Path("./")

    if config_path is None:
        config_path = Path(os.environ.get(ENV_CONFIG_PATH, here / "options.json"))

    options = None
    if config_path is not None and Path(config_path).is_file():
        with open(config_path, "r") as f:
            options = json.load(f)

    logger.info(f"reading options: {options}")

    # TODO Read and set EPD_TYPE constant

    settings = Settings(**options)
    logger.info(f"config: {settings}")
    return settings
