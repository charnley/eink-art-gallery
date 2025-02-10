import logging
from functools import cache

import torch
from diffusers import (
    AutoPipelineForText2Image,
    DiffusionPipeline,
    FluxPipeline,
    StableDiffusion3Pipeline,
)

from art_utils import constants

logger = logging.getLogger(__name__)

NEGATIVE_PROMPT = "paper, frame, picture frame, border, photorealistic, deformed, glitch, blurry, signature, signed, watermark, stamp"


def health_check():
    return torch.cuda.is_available()


@cache
def load_sd3(straight_to_gpu=True):

    logger.info("Loading the slow model from disk...")

    pipe = StableDiffusion3Pipeline.from_pretrained(
        "stabilityai/stable-diffusion-3-medium-diffusers", torch_dtype=torch.float16
    )

    logger.info("Loading the fast model from disk...")
    if straight_to_gpu:
        logger.info("Loading the model to GPU")
        pipe.to("cuda")

    pipe.set_progress_bar_config(disable=True)  # Disable tdqm

    return pipe


@cache
def load_flux_schnell(straight_to_gpu=True, model_path="./models/flux1schnell"):

    pipe = FluxPipeline.from_pretrained(model_path, torch_dtype=torch.bfloat16)
    # pipe.enable_model_cpu_offload()
    pipe.enable_sequential_cpu_offload()  # offloads modules to CPU on a submodule level (rather than model level)

    return pipe


def prompt_flux_schnell(pipe, prompt, negative_prompt=NEGATIVE_PROMPT):

    logger.info("Generating picture from prompt, using negative prompts")

    image = pipe(
        prompt,
        # negative_prompt=negative_prompt, # not supported
        guidance_scale=0.0,
        output_type="pil",
        num_inference_steps=4,
        max_sequence_length=256,
        width=960,
        height=688,
    ).images[0]

    image = image.resize((constants.WIDTH, constants.HEIGHT))  # ensure right resolution

    return image


def prompt_sd3(pipe, prompt, negative_prompt=NEGATIVE_PROMPT):

    negative_prompt = "paper, frame, picture frame, border, photorealistic, deformed, glitch, blurry, noisy, off-center, picture-frame, poster, signature"

    logger.info("Generating picture from prompt, using negative prompts")

    image = pipe(
        prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=28,
        guidance_scale=7.0,
        num_images_per_prompt=1,
        width=960,
        height=688,
    ).images[0]

    image = image.resize((constants.WIDTH, constants.HEIGHT))  # ensure right resolution

    return image
