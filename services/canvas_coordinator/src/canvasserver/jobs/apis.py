import logging
import threading
from io import BytesIO

import requests
from shared_constants import WaveshareDisplay
from shared_image_utils.dithering import atkinson_dither
from shared_image_utils.tasks import color_correct_red

logger = logging.getLogger(__name__)


def request_task(url, params, files, json):
    response = requests.post(url, params=params, files=files, json=json)
    logger.info(f"send and received: {response.status_code}")


def fire_and_forget_images(url, params, files):
    threading.Thread(target=request_task, args=(url, params, files, None)).start()


def send_image_to_device(image, display_model: WaveshareDisplay, hostname: str) -> bool:

    url = f"http://{hostname}/display/image"
    logger.info(f"Sending photo to {url}")

    logger.info(f"dithering the picture for {display_model}")

    # TODO Color correct for color palette, like grey

    if display_model == WaveshareDisplay.WaveShare13BlackRedWhite960x680:
        image = color_correct_red(image, dither=True)

    elif display_model == WaveshareDisplay.WaveShare13BlackWhite960x680:
        image = atkinson_dither(image)

    logger.info("Sending it to paper frame")
    byte_io = BytesIO()
    image.save(byte_io, "png")
    byte_io.seek(0)

    try:
        r = requests.post(url=url, files=dict(file=("service.png", byte_io, "image/png")))
        logger.info(r)
        return True

    except requests.exceptions.ConnectionError:
        logger.error(f"Could not send image to {url}")

    return False


def get_status(hostname):
    url = f"http://{hostname}/status"

    try:
        r = requests.get(url=url)
        status_code = r.status_code

        if status_code != 200:
            return None

        return r.json()

    except Exception:
        logger.error(f"not a real hostname: {hostname}")

    return None
