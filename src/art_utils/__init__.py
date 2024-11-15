import numpy as np
from numba import jit
from PIL import Image


@jit
def set_atkinson_dither_array(img: np.ndarray):
    """changes img array with atkinson dithering"""

    low = 0
    heigh = 255

    frac = 8  # Atkinson constant
    neighbours = np.array([[1, 0], [2, 0], [-1, 1], [0, 1], [1, 1], [0, 2]])
    threshold = np.zeros(256, dtype=np.int32)
    threshold[128:] = 255
    height, width = img.shape
    for y in range(height):
        for x in range(width):
            old = img[y, x]
            old = np.min(np.array([old, 255]))
            new = threshold[old]
            err = (old - new) // frac
            img[y, x] = new
            for dx, dy in neighbours:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    # Make sure that img set is between 0 and 255 (negative error could surpass the value)
                    img_yx = img[ny, nx] + err
                    img_yx = np.minimum(heigh, np.maximum(img_yx, low))
                    img[ny, nx] = img_yx


def palette_to_thresholds(palette: np.ndarray):

    # Calculate threshold array from palette
    thresholds = np.arange(256, dtype=np.int32)
    diff = np.abs(np.subtract.outer(palette, thresholds))
    closest = diff.argmin(axis=0)
    thresholds = palette[closest]
    return thresholds


@jit
def set_atkinson_dither_array_palette(img: np.ndarray, thresholds: np.ndarray):
    """changes img array with atkinson dithering"""

    heigh = 255
    low = 0

    frac = 8  # Atkinson constant
    neighbours = np.array([[1, 0], [2, 0], [-1, 1], [0, 1], [1, 1], [0, 2]])  # atkinson neighbours

    height, width = img.shape
    for y in range(height):
        for x in range(width):
            old = img[y, x]
            old = np.min(np.array([old, 255]))

            new = thresholds[old]  # look up palette conversion

            err = (old - new) // frac
            img[y, x] = new
            for dx, dy in neighbours:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    # Make sure that img set is between 0 and 255 (negative error could surpass the value)
                    img_yx = img[ny, nx] + err
                    img_yx = np.minimum(heigh, np.maximum(img_yx, low))
                    img[ny, nx] = img_yx


def atkinson_dither(image: Image.Image) -> Image.Image:
    """ """
    img = np.array(image.convert("L"), dtype=np.int32)
    set_atkinson_dither_array(img)
    return Image.fromarray(np.uint8(img))


def atkinson_dither_with_palette(image: Image.Image, pallete: np.ndarray):

    img = np.array(image.convert("L"), dtype=np.int32)
    thresholds = palette_to_thresholds(pallete)
    set_atkinson_dither_array_palette(img, thresholds)

    return Image.fromarray(np.uint8(img))


def image_split_red_channel(image: Image):

    data = image.getdata()

    r = [((d[0] - d[1] - d[2]), 0, 0) for d in data]
    r = [(d[0], d[0], d[0]) for d in r]
    gb = [(d[0], d[1], d[2]) for d in data]

    gb = [(dgb[0] - dr[0], dgb[1], dgb[2]) for dr, dgb in zip(r, gb)]

    image_r = image.copy()
    image_r.putdata(r)

    image_gb = image.copy()
    image_gb.putdata(gb)

    return image_r, image_gb
