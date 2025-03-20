import logging
import warnings

from desktop_server import network_utils
from desktop_server.art_generator import (
    load_flux_schnell,
    load_sd3,
    prompt_flux_schnell,
    prompt_sd3,
)
from rich.console import Console
from rich.logging import RichHandler
from shared_image_utils.dithering import atkinson_dither, image_split_red_channel

warnings.filterwarnings("ignore", category=UserWarning)
logger = logging.getLogger(__name__)


def push_picture(args):

    # Generate random prompt first
    if args.prompt is None:
        logger.info("Generating a random prompt")
        prompt = "ink drawing, man yelling, with sign saying 'prompt not found'"

    else:
        prompt = " ".join(args.prompt)

    logger.info(f"prompt: {prompt}")
    logger.info("Generating a random photo")

    load_func = None
    prompt_func = None

    if args.use_red:
        logger.info("Add some red")
        prompt = prompt.replace("bw", "bw and red")

    if args.method == "SD3":
        load_func = load_sd3
        prompt_func = prompt_sd3

    elif args.method == "FluxSchnell":
        load_func = load_flux_schnell
        prompt_func = prompt_flux_schnell

    assert load_func is not None
    assert prompt_func is not None

    # okay
    pipe = load_func()
    image = prompt_func(pipe, prompt)

    # Free GPU Mem
    del pipe

    # Dither

    if args.use_red:
        logger.info("splitting and dithering the picture")
        image_r, image_b = image_split_red_channel(image)
        image_r = atkinson_dither(image_r)
        image_b = atkinson_dither(image_b)
        logger.info("Sending it to red paper frame")
        r = network_utils.send_photo_red(image_b, image_r, f"{args.url}/display/redImage")

    else:
        logger.info("dithering the picture")
        logger.info("Sending it to paper frame")
        image = atkinson_dither(image)
        r = network_utils.send_photo(image, f"{args.url}/display/image")

    logger.info(f"Got {r} after {r.elapsed.total_seconds()} seconds")


def main(args=None):

    import argparse

    FORMAT = "%(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler(console=Console(width=89))],
    )

    parser = argparse.ArgumentParser()

    parser.add_argument("--prompt", type=str, default=None, nargs="+")
    parser.add_argument("--method", type=str, default="SD3", choices=["SD3", "FluxSchnell"])
    parser.add_argument("--use-red", action="store_true", default=False)
    parser.add_argument("--url", type=str)

    args = parser.parse_args(args)

    assert args.url is not None

    push_picture(args)


if __name__ == "__main__":
    main()
