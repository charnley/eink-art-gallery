import logging

from fastapi import APIRouter, Request
from fastapi.responses import Response
from shared_constants import IMAGE_CONTENT_TYPE, IMAGE_HEADER, WaveshareDisplay
from shared_image_utils import image_to_bytes
from shared_image_utils.displaying import prepare_image
from shared_matplotlib_utils import get_basic_404, get_basic_text

logger = logging.getLogger(__name__)

prefix = "/displays"
endpoint_queue = "/queue.png"

router = APIRouter(prefix=prefix, tags=["displays"])


@router.get(
    "/status.png", responses={200: {"content": {IMAGE_CONTENT_TYPE: {}}}}, response_class=Response
)
async def _get_status(request: Request):

    display_type = WaveshareDisplay.WaveShare13BlackWhite960x680
    image = get_basic_text("Today.", width=display_type.width, height=display_type.height)
    image = prepare_image(image, display_type)
    image_bytes = image_to_bytes(image)
    return Response(image_bytes, headers=IMAGE_HEADER, media_type=IMAGE_CONTENT_TYPE)


@router.get("/404.png", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
async def _get_404():

    display_type = WaveshareDisplay.WaveShare13BlackWhite960x680
    image = get_basic_404(None, width=display_type.width, height=display_type.height)
    image = prepare_image(image, display_type)
    image_bytes = image_to_bytes(image)
    return Response(image_bytes, headers=IMAGE_HEADER, media_type=IMAGE_CONTENT_TYPE)
