import logging
import warnings
from pathlib import Path

import requests
from desktop_server import network_utils
from desktop_server.art_generator import load_sd3, prompt_sd3
from rich.console import Console
from rich.logging import RichHandler
from shared_constants import FILE_UPLOAD_KEY, IMAGE_CONTENT_TYPE
from shared_image_utils import image_to_bytes

warnings.filterwarnings("ignore", category=UserWarning)
logger = logging.getLogger(__name__)

ENDPOINT_CHECK_PROMPTS = "/actions/prompts_check"
ENDPOINT_CHECK_THEMES = "/actions/theme_check"
ENDPOINT_UPLOAD_IMAGES = "/images"
ENDPOINT_UPLOAD_PROMPTS = "/prompts"


def refill_images(args):

    logger.info(f"Fetching from {args.server_url + ENDPOINT_CHECK_PROMPTS}")
    response = requests.get(args.server_url + ENDPOINT_CHECK_PROMPTS)

    assert response.status_code == 200, response.json()

    data = response.json()
    prompts = data["prompts"]

    logger.info(f"Got {len(prompts)} prompts need of refill...")

    # Nothing to do

    if data["count"] == 0:
        logger.info("Nothing todo... exiting")
        return

    # Load model
    load_func = load_sd3
    prompt_func = prompt_sd3

    pipe = load_func()

    for prompt in prompts:

        prompt_text = prompt["prompt"]
        prompt_id = prompt["id"]
        # prompt_model = prompt["model"]

        logger.info(f"Generating images for {prompt_id}...")

        # Generate images
        images = [prompt_func(pipe, prompt_text) for _ in range(args.fill_count)]

        files = [
            (FILE_UPLOAD_KEY, (f"file{i}", image_to_bytes(image), IMAGE_CONTENT_TYPE))
            for i, image in enumerate(images)
        ]

        logger.info(f"Uploading images for {prompt_id}...")
        params = dict(prompt=prompt_id)
        network_utils.fire_and_forget_images(
            args.server_url + ENDPOINT_UPLOAD_IMAGES, params, files
        )


def refill_prompts(args):

    # TODO auto-generated picture prompts

    # Read prompt file and put into database

    if args.prompts_filename is not None:

        logger.info("Reading pre-defined prompts...")

        with open(args.prompts_filename, "r") as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]

            prompts = [{"prompt": value, "model": "SD3"} for value in lines]

            for prompt in prompts:
                response = requests.post(args.server_url + ENDPOINT_UPLOAD_PROMPTS, json=prompt)
                logger.info(f"{response.status_code} {prompt}")

            logger.info(f"Database enriched with {len(lines)} prompts")


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

    parser.add_argument("--refill-images", action="store_true")
    parser.add_argument("--refill-prompts", action="store_true")
    parser.add_argument("--server-url", type=str)

    parser.add_argument("--fill-count", type=int, default=2)

    parser.add_argument("--prompts-filename", type=Path)

    args = parser.parse_args(args)

    assert args.server_url, "Need a server url to fetch and push to"

    if args.refill_prompts:
        refill_prompts(args)

    if args.refill_images:
        refill_images(args)


if __name__ == "__main__":
    main()
