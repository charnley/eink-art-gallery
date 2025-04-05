import logging
from pathlib import Path
import logging
import time
from pathlib import Path

from PIL import Image

from PIL.Image import Image as PilImage
from waveshare_epd import epd13in3b  # type: ignore
from waveshare_epd import epd13in3k  # type: ignore

logger = logging.getLogger(__name__)

logging.info("loaded epd13in3(K/B) picture api")


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


def display(image: PilImage, use_grey=False):
    logging.info(f"display pillow, using grey {use_grey}")
    epd = get_epd()

    if use_grey:
        epd.init_4GRAY()
        epd.display_4Gray(epd.getbuffer_4Gray(image))
        return

    epd.display(epd.getbuffer(image))


def display_red(image_red: PilImage, image_black: PilImage):
    logging.info("display pillow, using red")
    epd = get_epd(use_red=True)
    epd.display(epd.getbuffer(image_red), epd.getbuffer(image_black))


# def exit():
#    logging.info("epd exit")
#    epd13in3k.epdconfig.module_exit(cleanup=True)

def main(args=None):

    import argparse

    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--filename", action="store", help="", metavar="filename", type=Path
    )
    args = parser.parse_args(args)

    assert args.filename.is_file(), "Could not find file"

    image = Image.open(str(args.filename))

    assert image is not None, "Something wrong with the image"

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
