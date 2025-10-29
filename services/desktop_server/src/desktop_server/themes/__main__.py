import logging
import warnings
from pathlib import Path

import requests
from pydantic import BaseModel
from rich.console import Console
from rich.logging import RichHandler
from shared_constants import WaveshareDisplay

warnings.filterwarnings("ignore", category=UserWarning)
logger = logging.getLogger(__name__)

ENDPOINT_CREATE_PROMPTS = "/prompts/"


class PromptInput(BaseModel):
    filename: Path
    image_model: str
    display_model: WaveshareDisplay


class PromptPayload(BaseModel):
    prompt: str
    image_model: str
    display_model: WaveshareDisplay


def refill_prompts(prompts: list[PromptInput], server_url: str):

    # Read prompt file and put into database

    for prompt in prompts:

        with open(prompt.filename, "r") as f:
            lines = [line.strip() for line in f.readlines()]

        prompt_payloads = [
            PromptPayload(
                prompt=prompt_text,
                image_model=prompt.image_model,
                display_model=prompt.display_model,
            )
            for prompt_text in lines
        ]

        logger.info(f"Uploading to {server_url + ENDPOINT_CREATE_PROMPTS}")

        for payload in prompt_payloads:
            payload = payload.model_dump_json()
            response = requests.post(server_url + ENDPOINT_CREATE_PROMPTS, data=payload)
            logger.info(f"{response.status_code} {response.json()}")

        logger.info(f"Database enriched with {len(lines)} prompts")


def handlePromptInput(input):

    vars = input.split()

    assert len(vars) == 3

    filename = Path(vars[0])
    image_model = vars[1]
    display_model = WaveshareDisplay(vars[2])

    assert filename.is_file(), f"{filename} does not exist"

    return PromptInput(
        filename=filename,
        image_model=image_model,
        display_model=display_model,
    )


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

    parser.add_argument("--canvas-server-url", type=str)
    parser.add_argument("--prompts", type=str, nargs="+")
    args = parser.parse_args(args)

    prompts = [handlePromptInput(x) for x in args.prompts]

    assert args.canvas_server_url, "Need a server url to fetch and push to"

    # TODO Validate server status?

    refill_prompts(prompts, args.canvas_server_url)


if __name__ == "__main__":
    main()
