import logging
from functools import lru_cache
from pathlib import Path

from canvasserver.constants import MAX_DISK_SIZE, MIN_IMAGES_PER_PROMPT, MIN_PROMPTS_PER_THEME
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    app_name: str = "CanvasServer"
    database_path: Path = Path("./database.sqlite3")
    max_disk_size: int = MAX_DISK_SIZE
    min_images_per_prompt: int = MIN_IMAGES_PER_PROMPT
    min_prompts_per_theme: int = MIN_PROMPTS_PER_THEME


@lru_cache
def get_settings():
    s = Settings()
    logger.info(f"config: {s}")
    return s
