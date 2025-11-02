import numpy as np
from numba import jit
from PIL import Image
from PIL.Image import Image as PilImage


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


def atkinson_dither(image: PilImage) -> PilImage:
    img = np.array(image.convert("L"), dtype=np.int32)
    set_atkinson_dither_array(img)
    return Image.fromarray(np.uint8(img))


def atkinson_dither_with_palette(image: PilImage, palette: np.ndarray):
    img = np.array(image.convert("L"), dtype=np.int32)
    thresholds = palette_to_thresholds(palette)
    set_atkinson_dither_array_palette(img, thresholds)
    return Image.fromarray(np.uint8(img))


def atkinson_dither_rgb(image: PilImage, palette: np.ndarray) -> PilImage:

    _image = np.array(image.convert("RGB"), dtype=np.int32)
    dithered = atkinson_dither_rgb_numpy(_image, palette)

    return Image.fromarray(dithered.astype(np.uint8))


@jit
def nearest_color(color: np.ndarray, palette: np.ndarray):
    """Find nearest palette color (Euclidean distance)."""
    best_idx = 0
    best_dist = 1e9
    for i in range(palette.shape[0]):
        dr = int(color[0]) - int(palette[i, 0])
        dg = int(color[1]) - int(palette[i, 1])
        db = int(color[2]) - int(palette[i, 2])
        dist = dr * dr + dg * dg + db * db
        if dist < best_dist:
            best_dist = dist
            best_idx = i
    return palette[best_idx]


@jit
def atkinson_dither_rgb_numpy(img, palette):
    """In-place Atkinson dithering with multi-color palette."""
    frac = 8
    neighbours = np.array([[1, 0], [2, 0], [-1, 1], [0, 1], [1, 1], [0, 2]])

    h, w, c = img.shape
    for y in range(h):
        for x in range(w):
            old = img[y, x].copy()

            new = nearest_color(old, palette)
            img[y, x] = new
            err = (old - new) // frac

            for dx, dy in neighbours:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    for ch in range(3):  # distribute error per channel
                        v = int(img[ny, nx, ch]) + int(err[ch])
                        if v < 0:
                            v = 0
                        if v > 255:
                            v = 255
                        img[ny, nx, ch] = v
    return img
