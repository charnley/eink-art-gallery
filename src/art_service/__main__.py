
import logging

from art_generator import get_picture_fast, preload_fast_model
from art_utils.network_utils import send_photo

logger = logging.getLogger(__name__)

def main(args=None):

    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)

    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    args = parser.parse_args(args)

    logger.info("Hello World")

    # TODO Generate random prompt first
    logger.info("Generating a random prompt")
    prompt = "black and white, pen sketch, single lines, swiss mountains, spring, adventure, no background"

    logger.info("Generating a random photo")
    pipe = preload_fast_model()
    image = get_picture_fast(pipe, prompt)

    logger.info("Sending it to paper frame")
    send_photo(image, "http://192.168.1.26:8080/display/bitmap")

if __name__ == '__main__':
    main()
