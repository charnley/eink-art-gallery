import logging

import numpy as np
from canvasserver.jobs.apis import send_image_to_frame
from canvasserver.models.db_models import Frame, Image, Prompt
from canvasserver.models.schemas import Frames
from shared_constants import WaveshareDisplay
from shared_matplotlib_utils import get_basic_404
from sqlalchemy import func
from sqlmodel import select

logger = logging.getLogger(__name__)


def refresh_active_prompt(session):

    # TODO Need to create FrameGroup layer, finding active prompt per-group, and based on active Theme
    group_display_model = WaveshareDisplay.WaveShare13BlackWhite960x680
    no_group_frames = 6

    logger.info("Resetting active prompt")

    (session.query(Prompt).update({Prompt.active: False}, synchronize_session=False))

    _prompt = session.execute(
        select(Prompt)
        .filter(Prompt.display_model == group_display_model)  # type: ignore[arg-type]
        .join(Image, Image.prompt == Prompt.id, isouter=True)  # type: ignore[arg-type]
        .group_by(Prompt.id)
        .having(func.count(Image.id) >= no_group_frames)  # type: ignore[arg-type]
        .order_by(func.random())
    ).first()

    if _prompt is None:
        logger.warning("No prompts fulfilled the critia for active status")
        return None

    prompt = _prompt[0]
    prompt.active = True

    session.commit()

    logger.info(f"Setting active prompt: {prompt}")

    return prompt


def get_active_prompts(session):
    prompts: list[tuple[Prompt,]] = session.execute(select(Prompt).filter(Prompt.active)).all()  # type: ignore[arg-type]

    # TODO Again, group should do this
    group_display_model: WaveshareDisplay = WaveshareDisplay.WaveShare13BlackWhite960x680

    if len(prompts) == 0:
        logger.warning("No active prompts, returning all")
        prompts: list[tuple[Prompt,]] = session.execute(
            select(Prompt).filter(
                Prompt.display_model == group_display_model
            )  # type: ignore[arg-type]
        ).all()

    _prompts: list[Prompt] = [x[0] for x in prompts]
    prompt_ids = [str(prompt.id) for prompt in _prompts]

    return prompt_ids


def send_images_to_push_devices(session):

    raise NotImplementedError("Moved function")

    # TODO Should there be a group layer to push_devices?
    # TODO Collect status for push, and return
    # TODO Don't "use" image if push failed
    # TODO Change function to group

    results = session.execute(select(Frame)).all()
    devices = [result[0] for result in results]

    logger.info(devices)

    for device in devices:

        logger.info(f"Sending to image to: {device}")

        display_model = device.model

        results = (
            session.execute(
                select(Prompt)
                .filter_by(display_model=display_model)
                .outerjoin(Image, Image.prompt == Prompt.id)  # type: ignore[arg-type]
                .group_by(Prompt.id)
                .having(func.count(Image.id) >= 1)  # type: ignore[arg-type]
            )
        ).all()

        prompt_ids = [result[0].id for result in results]

        image = None
        image_obj = None

        if not len(prompt_ids):
            image = get_basic_404("", width=display_model.width, height=display_model.height)

        else:
            prompt_id = np.random.choice(prompt_ids)

            image_results = session.execute(
                select(Image).filter(Image.prompt == prompt_id).order_by(func.random())
            ).first()

            image_obj = image_results[0]
            image = image_obj.image
            session.delete(image_obj)

        status_code = send_image_to_frame(image, display_model, device.hostname)

        if status_code == 200 and image_obj is not None:
            session.delete(image_obj)

    return Frames(devices=devices, count=len(devices))
