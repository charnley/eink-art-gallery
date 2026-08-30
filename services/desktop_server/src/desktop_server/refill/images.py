import logging

from desktop_server.art_generator import load_sd3, prompt_sd3
from desktop_server.canvas_client import get_prompts_missing_images, upload_images
from shared_constants import WaveshareDisplay

logger = logging.getLogger(__name__)


def refill_images(server_url: str) -> None:
    """Fetch prompts missing images, generate them with SD3, upload back."""

    prompts = get_prompts_missing_images(server_url)

    logger.info(f"Got {len(prompts)} prompts need of refill...")

    # Nothing to do
    if len(prompts) == 0:
        logger.info("Nothing to do... exiting")
        return

    # Load model
    load_func = load_sd3
    prompt_func = prompt_sd3

    pipe = load_func()

    for prompt in prompts:

        # TODO Should use the pydantic model for prompts

        prompt_text = prompt["prompt"]
        prompt_id = prompt["id"]
        n_images = prompt["count_frames"] - prompt["count_images"]
        display_model = WaveshareDisplay(prompt["display_model"])

        width = display_model.width
        height = display_model.height

        logger.info(f"Generating {n_images} '{display_model}' images for '{prompt_id:10s}' ...")

        # Generate images
        images = [
            prompt_func(pipe, prompt_text, width=width, height=height) for _ in range(n_images)
        ]

        upload_images(server_url, prompt_id, images)
