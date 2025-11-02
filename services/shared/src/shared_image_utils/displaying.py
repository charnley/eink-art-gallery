from PIL.Image import Image as PilImage
from shared_constants import (
    WAVESHARE_BLACKWHITERED_PALETTE,
    WAVESHARE_FULLCOLOR_PALETTE,
    WaveshareDisplay,
)

from .dithering import atkinson_dither, atkinson_dither_rgb


def prepare_image(image: PilImage, display_model: WaveshareDisplay):

    if display_model == WaveshareDisplay.WaveShare13BlackRedWhite960x680:
        image = atkinson_dither_rgb(image, WAVESHARE_BLACKWHITERED_PALETTE)
        return image

    elif display_model == WaveshareDisplay.WaveShare13BlackWhite960x680:
        image = atkinson_dither(image)
        return image

    elif display_model == WaveshareDisplay.WaveShare13FullColor1600x1200:
        image = atkinson_dither_rgb(image, WAVESHARE_FULLCOLOR_PALETTE)
        return image

    raise ValueError("No recipe for display type")
