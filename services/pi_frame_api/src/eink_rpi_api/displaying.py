import logging
import time
from functools import cache
from pathlib import Path
from typing import Any

from PIL import Image
from PIL.Image import Image as PilImage
from shared_constants import WaveshareDisplay
from shared_image_utils.colors import steal_red_channel

logger = logging.getLogger(__name__)

# 13.3inch_e-Paper_K
# 13.3inch_e-Paper_B
# 13.3inch_e-Paper_E


EPD_TYPE: WaveshareDisplay


@cache
def find_epd():

    name = EPD_TYPE

    logging.info(f"loading {EPD_TYPE} waveshare epd...")

    epdlib = None

    if (
        name == WaveshareDisplay.WaveShare13BlackWhite960x680
        or name == WaveshareDisplay.WaveShare13BlackGreyWhite960x680
    ):
        from waveshare_epd import epd13in3k  # type: ignore

        epdlib = epd13in3k

    elif name == WaveshareDisplay.WaveShare13BlackRedWhite960x680:
        from waveshare_epd import epd13in3b  # type: ignore

        epdlib = epd13in3b

    elif name == WaveshareDisplay.WaveShare13FullColor1600x1200:
        from waveshare_epd_13in3e import epd13in3E  # type: ignore

        epdlib = epd13in3E

    assert epdlib is not None, "Unable to find the right WaveShare driver"

    return epdlib


def get_epd() -> Any:
    return find_epd().EPD()  # type: ignore


def sleep():
    logger.info("display sleep")
    epd = get_epd()
    epd.sleep()


def init():
    logging.info("display init")
    epd = get_epd()

    try:
        epd.init()
    except AttributeError:
        epd.Init()

    if EPD_TYPE == WaveshareDisplay.WaveShare13BlackGreyWhite960x680:
        epd.init_4GRAY()


def clear():
    logging.info("display clear")
    epd = get_epd()
    epd.Clear()


def display(image: PilImage) -> None:

    if EPD_TYPE == WaveshareDisplay.WaveShare13BlackWhite960x680:
        display_black(image)
        return

    elif EPD_TYPE == WaveshareDisplay.WaveShare13BlackGreyWhite960x680:
        display_grey(image)
        return

    elif EPD_TYPE == WaveshareDisplay.WaveShare13BlackRedWhite960x680:

        image_red, image_black = steal_red_channel(image)
        display_red(image_red, image_black)
        return

    elif EPD_TYPE == WaveshareDisplay.WaveShare13FullColor1600x1200:
        display_color(image)
        return

    logger.error(f"Unable to read the Waveshare EPD {EPD_TYPE}")
    raise ValueError(f"Wrong EPD type: {EPD_TYPE}")


def display_grey(image: PilImage):
    epd = get_epd()
    epd.display_4Gray(epd.getbuffer_4Gray(image))


def display_black(image: PilImage):
    epd = get_epd()
    epd.display(epd.getbuffer(image))


def display_red(image_red: PilImage, image_black: PilImage):
    logging.info("display pillow, using red")
    epd = get_epd()
    epd.display(epd.getbuffer(image_black), epd.getbuffer(image_red))


def display_color(image: PilImage):

    # Just following their example. Rotate the image 90 degrees clockwise
    image = image.transpose(Image.ROTATE_270)

    logging.info("display pillow, color")
    epd = get_epd()
    epd.display(epd.getbuffer(image))


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
        "--waveshare",
        action="store",
        help="",
        metavar="type",
        type=WaveshareDisplay,
        choices=list(WaveshareDisplay),
    )
    args = parser.parse_args(args)

    assert args.filename.is_file(), "Could not find file"

    image = Image.open(str(args.filename))

    assert image is not None, "Something wrong with the image"

    assert args.waveshare
    EPD_TYPE = args.waveshare

    epd = find_epd()
    assert epd is not None

    try:
        init()
        clear()
        display(image)
        time.sleep(20)
        clear()

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        exit()


if __name__ == "__main__":
    main()
