from enum import Enum

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


class ColorSupport(Enum):
    Black = "Black"
    BlackRed = "BlackRed"


EPD_RESOLUTIONS = {
    "WaveShare13BlackWhite960x680": (960, 680),
    "WaveShare13BlackGreyWhite960x680": (960, 680),
    "WaveShare13BlackRedWhite960x680": (960, 680),
    "WaveShare13FullColor1600x1200": (1600, 1200),
}


# Supported WaveShare displays
class WaveshareDisplay(Enum):
    WaveShare13BlackWhite960x680 = "WaveShare13BlackWhite960x680"
    WaveShare13BlackGreyWhite960x680 = "WaveShare13BlackGreyWhite960x680"
    WaveShare13BlackRedWhite960x680 = "WaveShare13BlackRedWhite960x680"
    WaveShare13FullColor1600x1200 = "WaveShare13FullColor1600x1200"

    @property
    def width(self):
        return EPD_RESOLUTIONS[self.value][0]

    @property
    def height(self):
        return EPD_RESOLUTIONS[self.value][1]
