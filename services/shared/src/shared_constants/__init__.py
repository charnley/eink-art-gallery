from enum import Enum

import numpy as np

# Default Image format
IMAGE_FORMAT = "PNG"
IMAGE_EXTENSION = "png"
IMAGE_CONTENT_TYPE = "image/png"

# Default Image settings
IMAGE_DPI = 96
IMAGE_WIDTH = 960
IMAGE_HEIGHT = 680

# Default font config
FONT_FAMILY = ["Cormorant", "NanumMyeongjo", "Segoe UI Emoji"]
FONT_FAMILY_MONO = "DejaVu Sans Mono"
FONT_WEIGHT = "bold"

# Date format
DATE_FORMAT = "%Y-%m-%d %H:%M"
DATE_FORMAT_SHORT = "%H:%M %d/%m"

# HTTP HEADERS
IMAGE_HEADER = {"Content-Disposition": f'inline; filename="image.{IMAGE_EXTENSION}"'}

# Server limitation
MAX_DISK_SIZE = 100  # mb
MIN_PROMPTS_PER_THEME = 3
MIN_IMAGES_PER_PROMPT = 2

# APIs
FILE_UPLOAD_KEY = "files"


class FrameType(str, Enum):
    PULL = "pull"
    PUSH = "push"

    def __str__(self) -> str:
        return self.name


DISPLAY_RESOLUTIONS = {
    "WaveShare7BlackWhite800x480": (800, 480),
    "WaveShare13BlackWhite960x680": (960, 680),
    "WaveShare13BlackGreyWhite960x680": (960, 680),
    "WaveShare13BlackRedWhite960x680": (960, 680),
    "WaveShare13FullColor1600x1200": (1600, 1200),
}


# Supported WaveShare displays
class WaveshareDisplay(Enum):
    WaveShare7BlackWhite800x480 = "WaveShare7BlackWhite800x480"
    WaveShare13BlackWhite960x680 = "WaveShare13BlackWhite960x680"
    WaveShare13BlackGreyWhite960x680 = "WaveShare13BlackGreyWhite960x680"
    WaveShare13BlackRedWhite960x680 = "WaveShare13BlackRedWhite960x680"
    WaveShare13FullColor1600x1200 = "WaveShare13FullColor1600x1200"

    @property
    def width(self) -> int:
        return DISPLAY_RESOLUTIONS[self.value][0]

    @property
    def height(self) -> int:
        return DISPLAY_RESOLUTIONS[self.value][1]

    def __str__(self) -> str:
        return self.name


WAVESHARE_FULLCOLOR_PALETTE = np.array(
    [
        [0, 0, 0],  # Black
        [255, 255, 255],  # White
        [255, 255, 0],  # Yellow
        [255, 0, 0],  # Red
        [0, 0, 255],  # Blue
        [0, 255, 0],  # Green
    ],
    dtype=np.uint8,
)

WAVESHARE_BLACKWHITERED_PALETTE = np.array(
    [
        [0, 0, 0],  # Black
        [255, 255, 255],  # White
        [255, 0, 0],  # Red
    ],
    dtype=np.uint8,
)
