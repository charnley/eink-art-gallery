import logging
from io import BytesIO

import numpy as np
import requests
from canvasserver.jobs.apis import send_image_to_device, send_image_to_device_red
from canvasserver.models.content import ColorSupport, Image, Prompt, PushFrame, PushFrames
from canvasserver.models.db import get_session
from shared_image_utils.dithering import atkinson_dither, image_split_red_channel
from shared_matplotlib_utils import get_basic_404
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


def send_images_to_push_devices(session):

    results = session.execute(select(PushFrame)).all()

    devices = [result[0] for result in results]

    for device in devices:

        logger.info(f"Sending to {device}")

        color_mode = device.color_support

        results = (
            session.execute(
                select(Prompt)
                .filter_by(color_support=color_mode)
                .outerjoin(Image, Image.prompt == Prompt.id)
                .group_by(Prompt.id)
                .having(func.count(Image.id) >= 1)
            )
        ).all()

        prompt_ids = [result[0].id for result in results]

        image = None

        if not len(prompt_ids):
            image = get_basic_404("")

        else:
            prompt_id = np.random.choice(prompt_ids)

            image_results = session.execute(
                select(Image).filter(Image.prompt == prompt_id).order_by(func.random())
            ).first()

            image_obj = image_results[0]
            image = image_obj.image
            session.delete(image_obj)

        if color_mode == ColorSupport.BlackRed:
            send_image_to_device_red(image, device.hostname)

        else:
            # Default is black
            send_image_to_device(image, device.hostname)

    return PushFrames(devices=devices, count=len(devices))
