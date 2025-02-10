import logging
import site
import sys
from functools import cache
from pathlib import Path

from PIL.Image import Image
from waveshare_epd import epd13in3b  # type: ignore
from waveshare_epd import epd13in3k  # type: ignore

logger = logging.getLogger(__name__)

logging.info("epd13in3(K/B) picture api")


def get_epd(use_red=True):
    logger.info("epd loading")
    if use_red:
        return epd13in3b.EPD()
    return epd13in3k.EPD()


def sleep():
    logger.info("display sleep")
    epd = get_epd()
    epd.sleep()


def init():
    logging.info("display init")
    epd = get_epd()
    epd.init()


def clear():
    logging.info("display clear")
    epd = get_epd()
    epd.Clear()


def display(image: Image, use_grey=False):
    logging.info(f"display pillow, using grey {use_grey}")
    epd = get_epd()

    if use_grey:
        epd.init_4GRAY()
        epd.display_4Gray(epd.getbuffer_4Gray(image))
        return

    epd.display(epd.getbuffer(image))


def display_red(image_red: Image, image_black: Image):
    logging.info("display pillow, using red")
    epd = get_epd(use_red=True)
    epd.display(epd.getbuffer(image_red), epd.getbuffer(image_black))


# def exit():
#    logging.info("epd exit")
#    epd13in3k.epdconfig.module_exit(cleanup=True)
