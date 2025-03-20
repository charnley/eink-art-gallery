import logging
import threading
from io import BytesIO
from typing import Any

import requests
from PIL import Image

logger = logging.getLogger(__name__)


def request_task(url, params, files, json):
    response = requests.post(url, params=params, files=files, json=json)
    logger.info(f"send and received: {response.status_code}")


def fire_and_forget_images(url, params, files):
    threading.Thread(target=request_task, args=(url, params, files, None)).start()


# def fire_and_forget_post(url, params, json: dict[str, Any]):
#     threading.Thread(target=request_task, args=(url, params, None, json)).start()


def send_photo(image: Image.Image, url):
    """Send a photo to paper_api"""

    byte_io = BytesIO()
    image.save(byte_io, "png")
    byte_io.seek(0)

    return requests.post(url=url, files=dict(file=("service.png", byte_io, "image/png")))


def send_photo_red(image_red: Image.Image, image_black: Image.Image, url):
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
