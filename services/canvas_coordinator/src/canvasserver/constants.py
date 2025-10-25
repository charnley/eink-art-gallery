APP_NAME = "CanvasServer"

# Default Image format
IMAGE_FORMAT = "PNG"
IMAGE_EXTENSION = "png"
IMAGE_CONTENT_TYPE = "image/png"

# Default Image settings
IMAGE_DPI = 96
IMAGE_WIDTH: int = 960
IMAGE_HEIGHT: int = 680

# Default font config
FONT_FAMILY = "Fira Sans"
FONT_WEIGHT = "bold"

# Date format
DATE_FORMAT = "%Y-%m-%d %H:%M"

# HTTP HEADERS
IMAGE_HEADER = {"Content-Disposition": f'inline; filename="image.{IMAGE_EXTENSION}"'}

# Server limitation
MAX_DISK_SIZE = 100  # mb
MIN_PROMPTS_PER_THEME = 3
MIN_IMAGES_PER_PROMPT = 2

# Environ keys
ENV_CONFIG_PATH = "CONFIG_PATH"
ENV_DATA_PATH = "STORAGE"

# Options keys
LOG_LEVEL = "log_level"
CRON_UPDATE_PUSH = "cron_update_push"
CRON_UPDATE_PROMPT = "cron_update_prompt"

# Default frame cron
DEFAULT_PULLFRAME_CRON = "30 4 * * *"
DEFAULT_PULLFRAME_GROUP_NAME = "default_pullframe_group"
