import logging

import requests
from desktop_server import network_utils
from PIL import Image
from pydantic import BaseModel
from shared_constants import FILE_UPLOAD_KEY, IMAGE_CONTENT_TYPE, WaveshareDisplay
from shared_image_utils import image_to_bytes

logger = logging.getLogger(__name__)

ENDPOINT_CREATE_PROMPTS = "/prompts/"
ENDPOINT_CHECK_PROMPTS = "/prompts/?filter=missing"
ENDPOINT_FRAMES = "/frames/"
ENDPOINT_UPLOAD_IMAGES = "/images/"


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


def get_prompts_missing_images(server_url: str) -> list[dict]:
    """Fetch prompts that still need images generated for them."""
    response = requests.get(server_url + ENDPOINT_CHECK_PROMPTS)
    response.raise_for_status()
    return response.json()["prompts"]


def upload_images(server_url: str, prompt_id: str, images: list[Image.Image]) -> None:
    """Upload generated images for a prompt (fire and forget)."""
    files = [
        (FILE_UPLOAD_KEY, (f"file{i}", image_to_bytes(image), IMAGE_CONTENT_TYPE))
        for i, image in enumerate(images)
    ]

    logger.info(f"Uploading {len(images)} images for {prompt_id}...")
    params = dict(prompt=prompt_id)
    network_utils.fire_and_forget_images(server_url + ENDPOINT_UPLOAD_IMAGES, params, files)


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
