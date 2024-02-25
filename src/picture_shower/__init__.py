import logging
import time
from functools import cache
from pathlib import Path

from PIL import Image
from waveshare_epd import epd13in3k  # type: ignore

logger = logging.getLogger(__name__)

logging.info("epd13in3k Demo")
# epd = epd13in3k.EPD()


@cache
def get_epd():
    epd = epd13in3k.EPD()
    return epd


def sleep():
    epd = get_epd()
    epd.sleep()


def clear():
    logging.info("init and Clear")
    epd = get_epd()
    epd.init()
    epd.Clear()


def display(image: Image.Image):
    logging.info("Displaying")
    epd = get_epd()
    epd.display(epd.getbuffer(image))
    time.sleep(2)
