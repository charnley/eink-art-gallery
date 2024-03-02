import logging
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

from art_generator import (
    get_picture_fast,
    get_picture_slow,
    preload_fast_model,
    preload_slow_model,
)
from art_utils import atkinson_dither
from art_utils.network_utils import send_photo

logger = logging.getLogger(__name__)


def main(args=None):

    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()

    parser.add_argument("--prompt", type=str, default=None, nargs="+")
    parser.add_argument("--fast", action=argparse.BooleanOptionalAction)

    args = parser.parse_args(args)

    logger.info("Hello World")

    # Generate random prompt first
    logger.info("Generating a random prompt")
    if args.prompt is None:
        prompt = "Enchanted Forest, Mystical, Glowing Flora, Fauna, Magical Creatures, black and white, single lines, no background"
    else:
        prompt = " ".join(args.prompt)

    logger.info(f"prompt: {prompt}")
    logger.info("Generating a random photo")

    if args.fast:
        pipe = preload_fast_model()
        image = get_picture_fast(pipe, prompt)
    else:
        pipe = preload_slow_model()
        image = get_picture_slow(pipe, prompt)

    # Dither
    logger.info("dithering the picture")
    image = atkinson_dither(image)

    logger.info("Sending it to paper frame")
    send_photo(image, "http://192.168.1.26:8080/display/bitmap")


if __name__ == "__main__":
    main()
