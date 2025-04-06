import logging
from io import BytesIO

import requests
from canvasserver.models.content import Image, Prompt
from canvasserver.models.db import get_session
from shared_image_utils.dithering import atkinson_dither, image_split_red_channel
from sqlalchemy import func
from sqlmodel import select

logger = logging.getLogger(__name__)


def refresh_active_prompt(session):

    no_frames = 6  # TODO Should be number of fitting reading_devices

    logger.info("Resetting active prompt")

    # TODO Which theme is active?

    (session.query(Prompt).update({Prompt.active: False}, synchronize_session=False))

    _prompt = session.execute(
        select(Prompt)
        .join(Image, Image.prompt == Prompt.id)
        .group_by(Prompt.id)
        .having(func.count(Image.id) >= no_frames)
        .order_by(func.random())
    ).first()

    if _prompt is None:
        logger.warning("No prompts fulfilled the critia for active status")
        # TODO Some service is lazy with the image refill
        return None

    prompt = _prompt[0]
    prompt.active = True

    session.commit()

    logger.info(f"Setting active prompt: {prompt}")

    return prompt


def get_active_prompts(session):
    prompts: list[tuple[Prompt,]] = session.execute(select(Prompt).filter(Prompt.active)).all()

    if len(prompts) == 0:
        logger.warning("No active prompts, returning all")
        prompts: list[tuple[Prompt,]] = session.execute(select(Prompt)).all()

    _prompts: list[Prompt] = [x[0] for x in prompts]
    prompt_ids = [str(prompt.id) for prompt in _prompts]

    return prompt_ids


def send_image_to_device(image, hostname):

    url = hostname + "/display/image"

    logger.info("dithering the picture")
    image = atkinson_dither(image)
    logger.info("Sending it to paper frame")
    byte_io = BytesIO()
    image.save(byte_io, "png")
    byte_io.seek(0)

    _ = requests.post(url=url, files=dict(file=("service.png", byte_io, "image/png")))


def send_image_to_device_red(image, hostname):

    url = hostname + "/display/imageRed"

    logger.info("splitting and dithering the picture")
    image_red, image_black = image_split_red_channel(image)
    image_red = atkinson_dither(image_red)
    image_black = atkinson_dither(image_black)
    logger.info("Sending it to red paper frame")

    byte_io_red = BytesIO()
    image_red.save(byte_io_red, "png")
    byte_io_red.seek(0)

    byte_io_black = BytesIO()
    image_black.save(byte_io_black, "png")
    byte_io_black.seek(0)

    _ = requests.post(
        url=url,
        files=dict(
            redFile=("red.png", byte_io_red, "image/png"),
            blackFile=("black.png", byte_io_black, "image/png"),
        ),
    )

    # TODO Check r error code


def send_images_to_push_devices(session):

    # TODO For push devices

    return
