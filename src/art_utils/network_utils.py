from io import BytesIO

import requests
from PIL import Image


def send_photo(image: Image.Image, url):
    """Send a photo to paper_api"""

    byte_io = BytesIO()
    image.save(byte_io, "bmp")
    byte_io.seek(0)

    return requests.post(url=url, files=dict(file=("service.bmp", byte_io, "image/bmp")))
