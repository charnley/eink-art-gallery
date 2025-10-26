import logging

import numpy as np
from canvasserver.jobs import get_active_prompts
from canvasserver.models.db_models import Frame, FrameGroup, Image, Prompt
from shared_constants import FrameType, WaveshareDisplay
from shared_matplotlib_utils import get_basic_404
from sqlalchemy import func
from sqlmodel import Session, select

logger = logging.getLogger(__name__)


def get_default_group(session):
    return session.query(FrameGroup).filter_by(default=True).first()


def register_frame_default_group(session: Session, frame: Frame) -> FrameGroup | None:

    group = session.query(FrameGroup).filter_by(default=True).first()

    if group is None:
        return None

    frame.group_id = group.id

    return group


def register_new_frame(session: Session, mac: str, display_model: WaveshareDisplay) -> Frame:

    # Register with default group

    default_group = get_default_group(session)
    group_id = default_group.id if default_group is not None else None

    frame = Frame(
        mac=mac,
        model=display_model,
        group_id=group_id,
        type=FrameType.PULL,
    )

    session.add(frame)

    return frame


def get_frame_by_mac_address(
    session, mac_address, display_model: WaveshareDisplay | None
) -> Frame | None:

    frame = session.query(Frame).filter_by(mac=mac_address).first()

    if frame is not None:
        return frame

    elif frame is None and display_model is None:
        return None

    elif frame is None and isinstance(display_model, WaveshareDisplay):
        # Register new frame
        logger.info("Found new frame, registering")
        frame = register_new_frame(session, mac_address, display_model)
        session.commit()
        return frame

    logger.error("This shouldn't be possible")
    raise ValueError("Not possible to handle frame registration")


def fetch_image_for_frame(session, frame):

    display_model = frame.model

    prompt_ids = get_active_prompts(session, frame.model)

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
        image = get_basic_404(
            "No active prompts", width=display_model.width, height=display_model.height
        )
        return image

    prompt_id = np.random.choice(prompt_ids)

    image_results = session.execute(
        select(Image).filter(Image.prompt == prompt_id).order_by(func.random())
    ).first()

    image_obj = image_results[0]
    image = image_obj.image
    session.delete(image_obj)

    return image
