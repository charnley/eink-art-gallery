import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Union, Optional

from pydantic_settings import BaseSettings

from .constants import ENV_CONFIG_PATH
from .displaying import EpdType, EPD_TYPE

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    log_level: str = "INFO"
    cron_refresh: Optional[str] = None
    EPD_TYPE: EpdType


@lru_cache
def get_settings(config_path: Optional[Path] = None):

    global EPD_TYPE

    here = Path("./")

    if config_path is None:
        config_path = Path(os.environ.get(ENV_CONFIG_PATH, here / "options.json"))

    options = None
    if config_path is not None and Path(config_path).is_file():
        with open(config_path, "r") as f:
            options = json.load(f)

    logger.info(f"reading options: {options}")

    # TODO Read and set EPD_TYPE constant
    epd_type = EpdType(options["EPD_TYPE"])

    EPD_TYPE = EpdType(epd_type)
    assert EPD_TYPE is not None
    assert isinstance(EPD_TYPE, EpdType)

    settings = Settings(**options)

    settings.EPD_TYPE = EPD_TYPE

    logger.info(f"config: {settings}")
    return settings
