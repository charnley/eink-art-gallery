import logging

from canvasserver.image_utils import dithering, image_to_bytes
from canvasserver.models.content import Image
from canvasserver.models.db import get_session
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from shared_constants import IMAGE_CONTENT_TYPE, IMAGE_HEADER
from shared_matplotlib_utils import get_basic_404, get_basic_text
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
    image = get_basic_404("Image could not be found on server")
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
async def _get_queue(dry_run: bool = False, session: Session = Depends(get_session)):

    # TODO Check for reading_device, check for color and for size
    # TODO Check for current active prompt
    # TODO Set reading_device id as parameter for debugging

    # Get the next image
    image_obj = session.query(Image).order_by(func.random()).first()

    is_empty = image_obj is None

    if is_empty:
        image = get_basic_404("")
    else:
        image = image_obj.image

    if not dry_run and not is_empty:
        session.delete(image_obj)
        session.commit()
        count_left = session.query(Image).count()
        logger.info(f"Qurrent queue has {count_left} images")

    image = dithering.atkinson_dither(image)
    image_bytes = image_to_bytes(image)

    # TODO Check if ESPHome accepts files from 404

    return Response(
        image_bytes,
        headers=IMAGE_HEADER,
        media_type=IMAGE_CONTENT_TYPE,
        status_code=200 if not is_empty else 404,
    )
