import logging
import uuid

from canvasserver.facades import get_basic_404
from canvasserver.image_utils import dithering, image_to_bytes
from fastapi import APIRouter, Depends, HTTPException, Response
from PIL import Image
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..constants import IMAGE_CONTENT_TYPE, IMAGE_HEADER
from ..models.content import Image, Prompt
from ..models.db import get_session

logger = logging.getLogger(__name__)

prefix = "/actions"
router = APIRouter(prefix=prefix, tags=["actions"])


def _generate_image(prompt):

    response = requests.post(external_api_url, json={"prompt": prompt})

    if response.status_code != 200:
        return None

    image_data = requests.get(image_url).content  # Get the image content

    return Image.Image


@router.get("/fill_queue/{promptId}", response_model=None, tags=["actions"])
def set_items(promptId, session: Session = Depends(get_session)):

    prompt = session.get(Prompt, id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Item not found")
    text = prompt.prompt

    # Connect to model, and fetch. Really. Should I use redis queue?
    task_id = str(uuid.uuid4())  # Generate a unique task ID for this request

    background_tasks.add_task(_generate_image, prompt.prompt, task_id)

    task_status[task_id] = {"status": "processing", "image_url": None}

    return


@router.get("/queue.png", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
async def _get_queue(dry_run: bool = False, session: Session = Depends(get_session)):

    # Get the next image
    image_obj = session.query(Image).order_by(func.random()).first()

    is_empty = image_obj is None

    if is_empty:
        image = get_basic_404("Queue is empty")
    else:
        image = image_obj.image

    if not dry_run and not is_empty:
        session.delete(image_obj)
        session.commit()
        count_left = session.query(Image).count()
        print(f"Qurrent queue has {count_left} images")

    image = dithering.atkinson_dither(image)
    image_bytes = image_to_bytes(image)

    # TODO Check if ESPHome accepts files from 404

    return Response(
        image_bytes,
        headers=IMAGE_HEADER,
        media_type=IMAGE_CONTENT_TYPE,
        status_code=200 if not is_empty else 404,
    )
