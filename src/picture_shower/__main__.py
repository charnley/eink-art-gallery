import logging
import time
from pathlib import Path

from PIL import Image
from waveshare_epd import epd13in3k  # type: ignore

import picture_shower


def main(args=None):

    import argparse

    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--filename", action="store", help="", metavar="filename.bmp", type=Path
    )
    args = parser.parse_args(args)

    assert args.filename.is_file(), "Could not find file"
    assert args.filename.suffix == ".bmp", "can only load bitmaps"

    image = Image.open(str(args.filename))

    assert image is not None, "Something wrong with the image"

    try:

        picture_shower.clear()
        picture_shower.display(image)
        time.sleep(20)
        picture_shower.clear()

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd13in3k.epdconfig.module_exit(cleanup=True)
        exit()


if __name__ == "__main__":
    main()
