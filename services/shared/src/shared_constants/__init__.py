# Default Image format
IMAGE_FORMAT = "PNG"
IMAGE_EXTENSION = "png"
IMAGE_CONTENT_TYPE = "image/png"

# Default Image settings
IMAGE_DPI = 96
IMAGE_WIDTH = 960
IMAGE_HEIGHT = 680

# Default font config
FONT_FAMILY = "Fira Sans"
FONT_FAMILY_MONO = "DejaVu Sans Mono"
FONT_WEIGHT = "bold"

# Date format
DATE_FORMAT = "%Y-%m-%d %H:%M"

# HTTP HEADERS
IMAGE_HEADER = {"Content-Disposition": f'inline; filename="image.{IMAGE_EXTENSION}"'}

# Server limitation
MAX_DISK_SIZE = 100  # mb
MIN_PROMPTS_PER_THEME = 3
MIN_IMAGES_PER_PROMPT = 2

# APIs
FILE_UPLOAD_KEY = "files"
