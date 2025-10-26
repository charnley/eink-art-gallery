import logging

import numpy as np
from canvasserver.jobs.apis import send_image_to_frame
from canvasserver.models.db_models import Frame, Image, Prompt
from canvasserver.models.schemas import FrameHttpCode
from shared_matplotlib_utils import get_basic_404
from sqlalchemy import func
from sqlmodel import select

logger = logging.getLogger(__name__)


def send_images_to_push_frames(frames: list[Frame], session) -> list[FrameHttpCode]:

    # TODO There is no logic between group and theme/prompt, there probably should be

    returns = []

    for frame in frames:

        if frame.endpoint is None:
            continue

        logger.info(f"Sending to image to: {frame}")

        display_model = frame.model

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

        status_code = send_image_to_frame(image, frame)

        if status_code == 200 and image_obj is not None:
            session.delete(image_obj)

        returns.append(FrameHttpCode(id=frame.id, status_code=status_code))

    return returns
