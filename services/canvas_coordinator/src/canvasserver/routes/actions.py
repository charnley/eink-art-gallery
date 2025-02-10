import logging

from canvasserver.facades import get_basic_404
from canvasserver.image_utils import dithering, image_to_bytes
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..constants import IMAGE_CONTENT_TYPE, IMAGE_HEADER
from ..models.content import Image, Prompt, Prompts
from ..models.db import get_session

logger = logging.getLogger(__name__)

prefix = "/actions"
endpoint_queue = "/queue.png"

router = APIRouter(prefix=prefix, tags=["actions"])


@router.get(
    endpoint_queue,
    responses={
        200: {"content": {"image/png": {}}},
        404: {"content": {"image/png": {}}},
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


@router.get("/clean_up", response_model=None, tags=["actions"])
def _clean_up(session: Session = Depends(get_session)):
    # TODO Check if prompts needs to be updated
    # TODO Check if prompts are irrelevant
    return


@router.get("/queue_check", response_model=Prompts, tags=["actions"])
def _check_prompts(session: Session = Depends(get_session)):
    MIN_IMAGES = 5
    query = (
        session.query(Prompt)
        .outerjoin(Image, Image.prompt == Prompt.id)
        .group_by(Prompt.id)
        .having(func.count(Image.id) < MIN_IMAGES)
    )
    prompts = query.all()
    return Prompts(prompts=prompts, count=len(prompts))


@router.get("/theme_check", response_model=None, tags=["actions"])
def _check_themes(session: Session = Depends(get_session)):
    return Response()
