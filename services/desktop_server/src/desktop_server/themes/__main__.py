import logging
import warnings
from pathlib import Path

import requests
from rich.console import Console
from rich.logging import RichHandler

warnings.filterwarnings("ignore", category=UserWarning)
logger = logging.getLogger(__name__)

ENDPOINT_CHECK_THEMES = "/actions/theme_check"
ENDPOINT_UPLOAD_PROMPTS = "/prompts/"


def refill_prompts(args):

    # TODO auto-generated picture prompts

    # Read prompt file and put into database

    for filename, n_images, color_support in zip(
        args.prompts_filenames, args.prompts_n_images, args.prompts_colors
    ):

        logger.info("Reading pre-defined prompts...")

        with open(filename, "r") as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]

            prompts = [
                {
                    "prompt": value,
                    "model": "SD3",
                    "min_images": n_images,
                    "color_support": color_support,
                }
                for value in lines
            ]

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

    parser.add_argument("--server-url", type=str)
    parser.add_argument("--prompts-filenames", type=Path, nargs="+")
    parser.add_argument("--prompts-n-images", type=int, nargs="+")
    parser.add_argument("--prompts-colors", type=str, nargs="+")

    args = parser.parse_args(args)

    assert args.server_url, "Need a server url to fetch and push to"

    refill_prompts(args)


if __name__ == "__main__":
    main()
