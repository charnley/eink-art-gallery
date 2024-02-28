import logging
import site
import sys
from functools import cache
from pathlib import Path

import epaper
from PIL import Image

# import waveshare_epd
from waveshare_epd import epd13in3k  # type: ignore

# epaper_path = Path(site.getsitepackages()[0]) / "epaper/e-Paper/RaspberryPi_JetsonNano/python/lib"
# sys.path.append(str(epaper_path))


logger = logging.getLogger(__name__)

logging.info("epd13in3k Demo")
# epd = epd13in3k.EPD()


@cache
def get_epd():
    epd = epd13in3k.EPD()
    # epd = epaper.epaper("epd13in3k").EPD()
    return epd


def sleep():
    epd = get_epd()
    epd.sleep()


def init():
    logging.info("init display")
    epd = get_epd()
    epd.init()


def clear():
    logging.info("clear display")
    epd = get_epd()
    epd.Clear()


def display(image: Image.Image):
    logging.info("display pillow")
    epd = get_epd()
    epd.display(epd.getbuffer(image))


def exit():
    logging.info("exit epd")
    epd13in3k.epdconfig.module_exit(cleanup=True)
