from typing import Union

import numpy as np
from PIL import Image, ImageOps


def steal_red_channel(image: Image.Image) -> Union[Image.Image, Image.Image]:

    red_enhance = 1.2
    greenblue_dehance = 0.6

    red_enhance = 1.0
    greenblue_dehance = 0.5

    # Get red channel as white
    data2 = np.array(image).astype(np.int16)
    r, g, b = data2[:, :, 0], data2[:, :, 1], data2[:, :, 2]
    new_r = (red_enhance * r - greenblue_dehance * (g + b)).astype(np.int16)
    np.clip(new_r, 0, 255, new_r)
    new_r = new_r.astype(np.uint8)

    image_red = Image.fromarray(new_r, mode="L")
    image_red = ImageOps.invert(image_red)

    image_black = image.convert("L")
    image_black = ImageOps.invert(image_black)
    black_channel = np.array(image_black).astype(np.uint16)

    black_channel = black_channel + new_r
    np.clip(black_channel, 0, 255, black_channel)
    black_channel = black_channel.astype(np.uint8)

    image_black = Image.fromarray(black_channel, mode="L")
    image_black = ImageOps.invert(image_black)

    return image_red, image_black


def image_split_red_channel(image: Image.Image):

    data: list[tuple[float, float, float]] = image.getdata()  # type: ignore

    r = [((int(d[0] * 1.2) - int(d[1] * 0.6 + d[2] * 0.6)), 0, 0) for d in data]
    r = [(np.clip(d[0], 0, 255), d[0], d[0]) for d in r]

    gb = [(d[0], d[1], d[2]) for d in data]
    gb = [(dgb[0] + dr[0], dgb[1] + dr[0], dgb[2] + dr[0]) for dr, dgb in zip(r, gb)]

    image_r = image.copy()
    image_r.putdata(r)

    image_gb = image.copy()
    image_gb.putdata(gb)

    image_gb = image_gb.convert("L")
    image_r = ImageOps.invert(image_r.convert("L"))

    return image_r, image_gb


def subtract_images(image1: Image.Image, image2: Image.Image):

    img1 = np.array(image1.convert("L"), dtype=np.int32)
    img2 = np.array(image2.convert("L"), dtype=np.int32)

    # Convert to bit array
    img1 = img1.clip(max=1)
    img2 = img2.clip(max=1)

    imgz = img1 - img2
    imgz = np.clip(imgz, 0, 1)

    return Image.fromarray(np.uint8(imgz))


def convert_color(image, color_index=0, invert=True):

    if invert:
        image = ImageOps.invert(image)

    width, height = image.size

    img1 = np.array(image.convert("L"), dtype=np.int32)
    img1.resize([1, width * height])

    rgb = []

    cols = img1[0]

    for data in cols:
        row = [0, 0, 0]
        row[color_index] = int(data)
        rgb.append(tuple(row))

    image2 = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    image2.putdata(rgb)
    image2.putalpha(image)

    return image2
