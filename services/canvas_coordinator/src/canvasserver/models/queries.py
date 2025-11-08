import logging

import numpy as np
from canvasserver.models.db_models import Frame, FrameGroup, FrameGroupPrompt, Image, Prompt
from canvasserver.models.schemas import ImageData, PromptId, PromptStatus
from shared_constants import FrameType, WaveshareDisplay
from shared_matplotlib_utils import get_basic_404
from sqlalchemy import delete, func
from sqlmodel import Session, select

logger = logging.getLogger(__name__)


def find_prompts_with_missing_images(session) -> list[PromptStatus]:
    """

    For each prompt,
    find number of images
    and compare to the count of frames with same displaymodel

    """

    frame_counts = (
        select(Frame.model, func.count(Frame.id).label("frame_count"))
        .group_by(Frame.model)
        .subquery()
    )

    query = (
        select(Prompt, func.count(Image.id).label("image_count"), frame_counts.c.frame_count)
        .outerjoin(Image, Image.prompt == Prompt.id)
        .join(frame_counts, frame_counts.c.model == Prompt.display_model)
        .group_by(Prompt.id, frame_counts.c.frame_count)
        .having(func.count(Image.id) < frame_counts.c.frame_count)
    )

    prompt_statues = []
    results = session.exec(query).all()
    for prompt, image_count, frame_count in results:

        result = PromptStatus(
            **prompt.dict(),
            count_images=image_count,
            count_frames=frame_count,
        )
        prompt_statues.append(result)

    return prompt_statues


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

    if frame:
        return frame

    if display_model is None:
        return None

    # Register new frame
    logger.info("Found new frame, registering")
    frame = register_new_frame(session, mac_address, display_model)
    session.commit()
    return frame


def atomic_fetch(session, prompt_id) -> ImageData | None:

    picked_cte = (
        select(Image.id)
        .where(Image.prompt == prompt_id)
        .order_by(func.random())
        .limit(1)
        .cte("picked")
    )

    stmt = delete(Image).where(Image.id.in_(select(picked_cte.c.id))).returning(Image)

    deleted_image = session.execute(stmt).scalars().first()

    if deleted_image:
        image = ImageData(**deleted_image.model_dump())
        image.image = deleted_image.image
        session.commit()
        return image

    return None


def fetch_image_for_frame(session, frame):

    display_model = frame.model

    if frame.group is None:
        image = get_basic_404(
            "NotImplementedError NoGroupError",
            width=display_model.width,
            height=display_model.height,
        )
        return image

    group_id = frame.group.id
    results = (
        session.execute(
            select(Prompt)
            .join(FrameGroupPrompt, FrameGroupPrompt.prompt_id == Prompt.id)
            .filter(FrameGroupPrompt.group_id == group_id)
            .filter(Prompt.display_model == display_model)
            .outerjoin(Image, Image.prompt == Prompt.id)  # type: ignore[arg-type]
            .group_by(Prompt.id)
            .having(func.count(Image.id) >= 1)  # at least one image
        )
    ).all()

    if not len(results):
        # No prompt, or no prompt with photos left
        image = get_basic_404(None, width=display_model.width, height=display_model.height)
        return image

    prompt_ids = [r[0].id for r in results]
    prompt_id = np.random.choice(prompt_ids)

    # Fetch and delete image atomically
    image_data = atomic_fetch(session, prompt_id)

    if image_data is None:
        image = get_basic_404(None, width=display_model.width, height=display_model.height)
        return image

    return image_data.image


def rotate_prompt_for_group(session, group: FrameGroup) -> list[Prompt]:

    prompts = []

    # Remove current relationships
    session.execute(delete(FrameGroupPrompt).where(FrameGroupPrompt.group_id == group.id))

    frames = group.frames

    if not len(frames):
        logger.warning("No frames in group")
        return []

    display_counts = dict()
    for frame in frames:
        display_counts[frame.model] = display_counts.get(frame.model, 0) + 1

    for display_model, n_frames in display_counts.items():
        prompt = find_prompt(session, display_model, n_frames)

        if prompt is None:
            logger.warning(f"No prompts found for display {display_model}")
            continue

        group_prompt = FrameGroupPrompt(
            group_id=group.id,
            prompt_id=prompt.id,
        )

        session.add(group_prompt)
        prompts.append(PromptId(prompt_id=prompt.id))

        logger.info(f"Activating {prompt} for {group.id}")

    return prompts


def find_prompt(session, display_model, min_images):

    _prompt = session.execute(
        select(Prompt)
        .filter_by(display_model=display_model)
        .join(Image, Image.prompt == Prompt.id, isouter=True)  # type: ignore[arg-type]
        .group_by(Prompt.id)
        .having(func.count(Image.id) >= min_images)  # type: ignore[arg-type]
        .order_by(func.random())
    ).first()

    if _prompt is None:
        return None

    return _prompt[0]


def get_group_prompts(session, group):

    results = (
        session.execute(
            select(Prompt)
            .join(FrameGroupPrompt, FrameGroupPrompt.prompt_id == Prompt.id)
            .filter(FrameGroupPrompt.group_id == group.id)
        )
    ).all()

    prompts = [result[0] for result in results]

    return prompts


def get_group_push_frames(session, group):

    return
