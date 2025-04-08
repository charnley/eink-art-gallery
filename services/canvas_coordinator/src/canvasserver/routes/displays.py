import logging
from typing import Any

import numpy as np
from canvasserver.image_utils import dithering, image_to_bytes
from canvasserver.jobs import get_active_prompts
from canvasserver.models.content import Image
from canvasserver.models.db import get_session
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from shared_constants import IMAGE_CONTENT_TYPE, IMAGE_HEADER
from shared_matplotlib_utils import get_basic_404, get_basic_text
from sqlalchemy import select
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
    session: Session = Depends(get_session),
):

    # Note: ESPHome will react to 404, so always return 200

    # TODO Check for reading_device, check for color and for size
    # TODO Check for current active prompt
    # TODO Set reading_device id as parameter for debugging

    logger.info("Fetching from queue")

    # TODO If no active prompt, fetch from any

    _image_obj: Any  # Type of execute .first is inconsistent None | Tuple[Item]

    # Get the next image
    if random:
        _image_obj = session.execute(select(Image).order_by(func.random())).first()

    else:
        prompt_ids = get_active_prompts(session)
        prompt_id = np.random.choice(prompt_ids)

        logger.info(f"Query prompt {prompt_id}")

        _image_obj = session.execute(
            select(Image).filter(Image.prompt == prompt_id).order_by(func.random())
        ).first()

    is_empty = _image_obj is None

    if is_empty:
        # Get 404 image, but still return 200, otherwise ESP32 will react to
        # the error code
        logger.error("Could not find image")
        image = get_basic_404("")

    else:
        image = _image_obj[0].image

    if not dry_run and not is_empty:
        image_obj = _image_obj[0]
        session.delete(image_obj)
        session.commit()

    image = dithering.atkinson_dither(image)
    image_bytes = image_to_bytes(image)

    session.close()

    return Response(
        image_bytes,
        headers=IMAGE_HEADER,
        media_type=IMAGE_CONTENT_TYPE,
        status_code=200,
    )
