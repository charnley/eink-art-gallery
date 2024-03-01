import logging
from functools import cache

import torch
from diffusers import AutoPipelineForText2Image, DiffusionPipeline

from art_utils import constants

logger = logging.getLogger(__name__)


def health_check():
    return torch.cuda.is_available()


@cache
def preload_fast_model(straight_to_gpu=True):
    """Return fast pipeline, e.i. stabilityai/sdxl-turbo"""

    logger.info("Loading the fast model from disk...")
    pipe = AutoPipelineForText2Image.from_pretrained(
        "stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16"
    )

    logger.info("Loading the fast model from disk...")
    if straight_to_gpu:
        logger.info("Loading the model to GPU")
        pipe.to("cuda")

    return pipe


@cache
def preload_slow_model(straight_to_gpu=True):
    """Return the slow and pretty model, e.i. stabilityai/stable-diffusion-xl-base-1.0"""

    logger.info("Loading the slow model")

    pipe = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16",
    )
    if straight_to_gpu:
        logger.info("Loading the model to GPU")
        pipe.to("cuda")

    return pipe


def style_scanner(pipe, prompt, num_images_per_prompt=4):

    images = []

    # I need to do it one-at-a-time because I have low mem on my gpu
    # for _ in range(num_images_per_prompt):

    images += pipe(
        prompt,
        # negative_prompt=negative_prompt,
        num_inference_steps=1,
        guidance_scale=0.0,
        num_images_per_prompt=num_images_per_prompt,
    ).images

    return images


def get_picture_fast(pipe, prompt):

    image = pipe(
        prompt,
        # negative_prompt=negative_prompt,
        width=constants.WIDTH,
        height=constants.HEIGHT,
        num_inference_steps=1,
        guidance_scale=0.0,
        num_images_per_prompt=1,
    ).images[0]

    return image


def get_picture_slow(pipe, prompt):

    image = pipe(
        prompt,
        width=constants.WIDTH,
        height=constants.HEIGHT,
        num_images_per_prompt=1,
    ).images[0]

    return image


def prompt_generator():
    raise NotImplementedError()
