import logging

from canvasserver.models.content import Image, Prompt
from canvasserver.models.db import get_session
from sqlalchemy import func

logger = logging.getLogger(__name__)


def refresh_active_prompt():

    no_frames = 6  # TODO Should be number of fitting reading_devices

    logger.info("Resetting active prompt")

    session = get_session()

    # TODO Which theme is active?

    (session.query(Prompt).update({Prompt.active: False}, synchronize_session=False))

    prompt = (
        session.query(Prompt)
        .join(Image, Image.prompt == Prompt.id)
        .group_by(Prompt.id)
        .having(func.count(Image.id) >= no_frames)
        .order_by(func.random())
        .first()
    )

    if prompt is None:
        # TODO Some service is lazy with the image refill
        return

    prompt.active = True

    session.commit()

    logger.info(f"Setting {prompt}")

    return


def get_active_prompts():
    session = get_session()
    prompts = session.query(Prompt).filter(Prompt.active).all()
    prompt_ids = [str(prompt.id) for prompt in prompts]
    return prompt_ids


def send_images_to_push_devices():

    return
