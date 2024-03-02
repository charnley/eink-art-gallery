import numpy as np
from PIL import Image


def atkinson_dither(image: Image.Image) -> Image.Image:
    """ """
    frac = 8  # Atkinson constant
    neighbours = [(1, 0), (2, 0), (-1, 1), (0, 1), (1, 1), (0, 2)]
    img = np.array(image.convert("L"), dtype=np.int32)
    threshold = np.zeros(256, dtype=np.int32)
    threshold[128:] = 255
    height, width = img.shape
    for y in range(height):
        for x in range(width):
            old = img[y, x]
            old = np.min([old, 255])
            new = threshold[old]
            err = (old - new) // frac
            img[y, x] = new
            for dx, dy in neighbours:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    # Make sure that img set is between 0 and 255 (negative error could surpass the value)
                    img[ny, nx] = np.clip(img[ny, nx] + err, 0, 255)
    return Image.fromarray(np.uint8(img))
