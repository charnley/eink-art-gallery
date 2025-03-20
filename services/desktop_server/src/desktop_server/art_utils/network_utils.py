from io import BytesIO

import requests
from PIL.Image import Image


def send_photo(image: Image, url):
    """Send a photo to paper_api"""

    byte_io = BytesIO()
    image.save(byte_io, "png")
    byte_io.seek(0)

    return requests.post(url=url, files=dict(file=("service.png", byte_io, "image/png")))


def send_photo_red(image_red: Image, image_black: Image, url):
    """Send a photo to paper_api"""

    byte_io_red = BytesIO()
    image_red.save(byte_io_red, "png")
    byte_io_red.seek(0)

    byte_io_black = BytesIO()
    image_black.save(byte_io_black, "png")
    byte_io_black.seek(0)

    return requests.post(
        url=url,
        files=dict(
            redFile=("red.png", byte_io_red, "image/png"),
            blackFile=("black.png", byte_io_black, "image/png"),
        ),
    )
