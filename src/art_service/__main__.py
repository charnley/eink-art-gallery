import logging
import warnings

from art_generator import load_flux_schnell, load_sd3, prompt_flux_schnell, prompt_sd3
from art_utils import atkinson_dither
from art_utils.network_utils import send_photo

warnings.filterwarnings("ignore", category=UserWarning)
logger = logging.getLogger(__name__)


def main(args=None):

    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()

    parser.add_argument("--prompt", type=str, default=None, nargs="+")
    parser.add_argument("--method", type=str, default="SD3", choices=["SD3", "FluxSchnell"])

    args = parser.parse_args(args)

    # Generate random prompt first
    if args.prompt is None:
        logger.info("Generating a random prompt")
        prompt = "ink drawing, man yelling, with sign saying 'prompt not found'"

    else:
        prompt = " ".join(args.prompt)

    logger.info(f"prompt: {prompt}")
    logger.info("Generating a random photo")

    if args.method == "SD3":
        load_func = load_sd3
        prompt_func = prompt_sd3

    elif args.method == "FluxSchnell":
        load_func = load_flux_schnell
        prompt_func = prompt_flux_schnell

    # okay
    pipe = load_func()
    image = prompt_func(pipe, prompt)

    # Free GPU Mem
    del pipe

    # Dither
    logger.info("dithering the picture")
    image = atkinson_dither(image)

    logger.info("Sending it to paper frame")
    send_photo(image, "http://192.168.1.26:8080/display/image")

    image.save("test.bmp")


if __name__ == "__main__":
    main()
