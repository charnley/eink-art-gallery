import logging
import threading
from io import BytesIO

import requests
from shared_image_utils.dithering import atkinson_dither, image_split_red_channel

logger = logging.getLogger(__name__)


def request_task(url, params, files, json):
    response = requests.post(url, params=params, files=files, json=json)
    logger.info(f"send and received: {response.status_code}")


def fire_and_forget_images(url, params, files):
    threading.Thread(target=request_task, args=(url, params, files, None)).start()


def send_image_to_device(image, hostname):

    url = f"http://{hostname}/display/image"
    logger.info(f"Sending photo to {url}")

    logger.info("dithering the picture")
    image = atkinson_dither(image)
    logger.info("Sending it to paper frame")
    byte_io = BytesIO()
    image.save(byte_io, "png")
    byte_io.seek(0)

    r = requests.post(url=url, files=dict(file=("service.png", byte_io, "image/png")))

    logger.info(r)


def send_image_to_device_red(image, hostname):

    url = f"http://{hostname}/display/redImage"

    logger.info(f"Sending photo to {url}")
    logger.info("splitting and dithering the picture...")
    image_red, image_black = image_split_red_channel(image)
    image_red = atkinson_dither(image_red)
    image_black = atkinson_dither(image_black)
    logger.info("Sending it to red paper frame...")

    byte_io_red = BytesIO()
    image_red.save(byte_io_red, "png")
    byte_io_red.seek(0)

    byte_io_black = BytesIO()
    image_black.save(byte_io_black, "png")
    byte_io_black.seek(0)

    # TODO There is a error here, move the splitting to rpi

    # Do it async
    files = dict(
        redFile=("red.png", byte_io_black, "image/png"),
        blackFile=("black.png", byte_io_red, "image/png"),
    )

    fire_and_forget_images(url, None, files)


def get_status(hostname):
    url = f"http://{hostname}/status"

    try:
        r = requests.get(url=url)
        status_code = r.status_code
        return status_code == 200

    except Exception:
        logger.error(f"not a real hostname: {hostname}")

    return False
