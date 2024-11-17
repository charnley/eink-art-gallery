import logging
import warnings

from art_generator import load_flux_schnell, load_sd3, prompt_flux_schnell, prompt_sd3
from art_utils import atkinson_dither, image_split_red_channel
from art_utils.network_utils import send_photo, send_photo_red

warnings.filterwarnings("ignore", category=UserWarning)
logger = logging.getLogger(__name__)

URL = "http://192.168.1.26:8080"


def main(args=None):

    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()

    parser.add_argument("--prompt", type=str, default=None, nargs="+")
    parser.add_argument("--method", type=str, default="SD3", choices=["SD3", "FluxSchnell"])
    parser.add_argument("--use-red", action="store_true", default=False)

    args = parser.parse_args(args)

    # Generate random prompt first
    if args.prompt is None:
        logger.info("Generating a random prompt")
        prompt = "ink drawing, man yelling, with sign saying 'prompt not found'"

    else:
        prompt = " ".join(args.prompt)

    logger.info(f"prompt: {prompt}")
    logger.info("Generating a random photo")

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
        r = send_photo_red(image_b, image_r, f"{URL}/display/redImage")

    else:
        logger.info("dithering the picture")
        logger.info("Sending it to paper frame")
        image = atkinson_dither(image)
        r = send_photo(image, f"{URL}/display/image")

    logger.info(f"Got {r} after {r.elapsed.total_seconds()} seconds")
    image.save("test.bmp")


if __name__ == "__main__":
    main()
