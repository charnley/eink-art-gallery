import logging
from typing import Any

import numpy as np
from canvasserver.jobs import get_active_prompts
from canvasserver.models.content import Image
from canvasserver.models.db import get_session
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from shared_constants import IMAGE_CONTENT_TYPE, IMAGE_HEADER
from shared_image_utils import dithering, image_to_bytes
from shared_matplotlib_utils import get_basic_404, get_basic_text
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

prefix = "/displays"
endpoint_queue = "/queue.png"

router = APIRouter(prefix=prefix, tags=["displays"])


@router.get(
    "/status.png", responses={200: {"content": {IMAGE_CONTENT_TYPE: {}}}}, response_class=Response
)
async def _get_status():
    image = get_basic_text("I am alive")
    image = dithering.atkinson_dither(image)
    image_bytes = image_to_bytes(image)
    return Response(image_bytes, headers=IMAGE_HEADER, media_type=IMAGE_CONTENT_TYPE)


@router.get("/404.png", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
async def _get_404():
    image = get_basic_404("")
    image = dithering.atkinson_dither(image)
    image_bytes = image_to_bytes(image)
    return Response(image_bytes, headers=IMAGE_HEADER, media_type=IMAGE_CONTENT_TYPE)


@router.get(
    endpoint_queue,
    responses={
        200: {"content": {IMAGE_CONTENT_TYPE: {}}},
        404: {"content": {IMAGE_CONTENT_TYPE: {}}},
    },
    response_class=Response,
)
async def _get_queue(
    dry_run: bool = False,
    random: bool = False,
    queue: str | None = None,
    safe_http_code: bool | None = True,
    session: Session = Depends(get_session),
):
    # Note: ESPHome will react to 404, so always return 200
    status_code = 200
    _image_obj: Any  # Type of execute .first is inconsistent None | Tuple[Item]
    prompt_id = None

    # Get the next image
    if random:
        _image_obj = session.execute(
            delete(Image)
            .where(Image.id.in_(select(Image.id).order_by(func.random()).limit(1)))
            .returning(Image)
        ).fetchone()

    else:
        prompt_ids = get_active_prompts(session)
        prompt_id = np.random.choice(prompt_ids)

        logger.debug(f"Query prompt {prompt_id}")

        _image_obj = session.execute(
            delete(Image)
            .where(
                Image.id.in_(
                    select(Image.id)
                    .filter(Image.prompt == prompt_id)
                    .order_by(func.random())
                    .limit(1)
                )
            )
            .returning(Image)
        ).fetchone()

        if _image_obj is None:
            logger.error(f"Could not find image in {prompt_id}")

    if _image_obj is None:
        image = get_basic_404("")
        status_code = 404 if not safe_http_code else 200

    else:
        image = _image_obj[0].image

    image = dithering.atkinson_dither(image)
    image_bytes = image_to_bytes(image)

    session.commit()
    session.close()

    return Response(
        image_bytes,
        headers=IMAGE_HEADER,
        media_type=IMAGE_CONTENT_TYPE,
        status_code=status_code,
    )
