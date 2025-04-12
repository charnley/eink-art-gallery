from PIL import Image

from .colors import convert_color, steal_red_channel
from .dithering import atkinson_dither


def color_correct(image, colors, dither=True) -> Image.Image:

    # TODO Generalize to a pallet of colours

    width, height = image.size

    image1_r, image1_gb = steal_red_channel(image)

    if dither:
        image1_r = atkinson_dither(image1_r)
        image1_gb = atkinson_dither(image1_gb)

    composite = Image.new("RGBA", (width, height))
    composite.paste(image1_gb, (0, 0))
    red_channel = convert_color(image1_r, 0)
    composite.paste(red_channel, (0, 0), red_channel)

    return composite
