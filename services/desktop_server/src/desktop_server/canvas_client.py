import logging

import requests
from pydantic import BaseModel
from shared_constants import WaveshareDisplay

logger = logging.getLogger(__name__)

ENDPOINT_CREATE_PROMPTS = "/prompts/"


class PromptPayload(BaseModel):
    prompt: str
    image_model: str
    display_model: WaveshareDisplay


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
