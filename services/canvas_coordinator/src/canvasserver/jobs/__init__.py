import logging

from canvasserver.models.content import Image, Prompt
from canvasserver.models.db import get_session
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

    return
