import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from shared_constants import WaveshareDisplay

from .constants import ENV_CONFIG_PATH

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    log_level: str = "INFO"
    cron_refresh: Optional[str] = None
    EPD_TYPE: WaveshareDisplay


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

    if options:
        logger.info(f"reading options: {options}")

        # Read and set EPD_TYPE constant
        epd_type = WaveshareDisplay(options["EPD_TYPE"])
        assert isinstance(EPD_TYPE, WaveshareDisplay)

        options["EPD_TYPE"] = epd_type
        settings = Settings(**options)

    else:
        raise ValueError("Could not find any options to read")

    logger.info(f"config: {settings}")
    return settings
