import logging

import requests
from pydantic import BaseModel
from shared_constants import WaveshareDisplay

logger = logging.getLogger(__name__)

ENDPOINT_CREATE_PROMPTS = "/prompts/"
ENDPOINT_FRAMES = "/frames/"


class PromptPayload(BaseModel):
    prompt: str
    image_model: str
    display_model: WaveshareDisplay


def get_display_models(server_url: str) -> list[WaveshareDisplay]:
    """Fetch all frames from the canvas coordinator and return the unique display models registered."""
    response = requests.get(server_url + ENDPOINT_FRAMES)
    response.raise_for_status()
    frames = response.json()["frames"]
    return list({WaveshareDisplay(frame["model"]) for frame in frames})


def color_range_from_display(display: WaveshareDisplay) -> str:
    """Derive the color range (BW, BWR, COLOR) from the display model."""
    name = display.value
    if "FullColor" in name:
        return "COLOR"
    elif "Red" in name:
        return "BWR"
    else:
        return "BW"


def post_prompts(
    prompts: list[str],
    display_model: WaveshareDisplay,
    server_url: str,
    image_model: str = "SD3",
) -> None:
    logger.info(f"Uploading {len(prompts)} prompts to {server_url + ENDPOINT_CREATE_PROMPTS}")

    for prompt_text in prompts:
        payload = PromptPayload(
            prompt=prompt_text,
            image_model=image_model,
            display_model=display_model,
        )
        response = requests.post(
            server_url + ENDPOINT_CREATE_PROMPTS, data=payload.model_dump_json()
        )
        logger.info(f"{response.status_code} {response.json()}")

    logger.info(f"Uploaded {len(prompts)} prompts")
