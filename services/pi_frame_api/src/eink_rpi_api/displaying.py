import logging
import time
from enum import Enum
from functools import cache
from pathlib import Path
from typing import Union

from PIL import Image
from PIL.Image import Image as PilImage
from shared_image_utils.colors import steal_red_channel
from waveshare_epd import epd13in3b  # type: ignore
from waveshare_epd import epd13in3k  # type: ignore

logger = logging.getLogger(__name__)


class EpdType(Enum):
    Black13 = "Black13"
    BlackGrey13 = "BlackGrey13"
    BlackRed13 = "BlackRed13"


EPD_TYPE: EpdType = EpdType.Black13


@cache
def find_epd():

    name = EPD_TYPE

    logging.info(f"loaded {EPD_TYPE} waveshare epf")

    epdlib = None

    if name == EpdType.Black13 or name == EpdType.BlackGrey13:
        epdlib = epd13in3k

    elif name == EpdType.BlackRed13:
        epdlib = epd13in3b

    return epdlib


def get_epd() -> Union[epd13in3k.EPD, epd13in3b.EPD]:
    return find_epd().EPD()  # type: ignore


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


def display(image: PilImage) -> None:

    if EPD_TYPE == EpdType.Black13 or EPD_TYPE == EpdType.BlackGrey13:
        display_black(image)

    elif EPD_TYPE == EpdType.BlackRed13:

        # split image
        image_red, image_black = steal_red_channel(image)
        display_red(image_red, image_black)

    else:
        logger.error(f"Unable to read the Waveshare EPD {EPD_TYPE}")
        raise ValueError(f"Wrong EPD type: {EPD_TYPE}")

    return


def display_black(image: PilImage):
    epd: epd13in3k.EPD = get_epd()

    if EPD_TYPE == EpdType.BlackGrey13:
        epd.init_4GRAY()
        epd.display_4Gray(epd.getbuffer_4Gray(image))
        return

    epd.display(epd.getbuffer(image))


def display_red(image_red: PilImage, image_black: PilImage):
    logging.info("display pillow, using red")
    epd: epd13in3b.EPD = get_epd()
    epd.display(epd.getbuffer(image_black), epd.getbuffer(image_red))


# def exit():
#    logging.info("epd exit")
#    epd13in3k.epdconfig.module_exit(cleanup=True)


def main(args=None):

    global EPD_TYPE

    import argparse

    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", action="store", help="", metavar="filename", type=Path)
    parser.add_argument(
        "--waveshare", action="store", help="", metavar="type", type=EpdType, choices=list(EpdType)
    )
    args = parser.parse_args(args)

    assert args.filename.is_file(), "Could not find file"

    image = Image.open(str(args.filename))

    assert image is not None, "Something wrong with the image"

    EPD_TYPE = args.waveshare

    epd = find_epd()
    assert epd is not None

    try:
        clear()
        display(image)
        time.sleep(20)
        clear()

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        exit()


if __name__ == "__main__":
    main()
