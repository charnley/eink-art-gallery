from canvasserver.image_utils import dithering, image_to_bytes
from fastapi import APIRouter
from fastapi.responses import Response

from ..constants import IMAGE_EXTENSION, IMAGE_HEADER
from ..facades import get_basic_404, get_basic_text

router = APIRouter(prefix="/displays", tags=["displays"])


@router.get(
    "/status.png", responses={200: {"content": {"image/png": {}}}}, response_class=Response
)
async def _get_status():
    image = get_basic_text("I am alive")
    image = dithering.atkinson_dither(image)
    image_bytes = image_to_bytes(image)
    return Response(image_bytes, headers=IMAGE_HEADER, media_type=f"image/{IMAGE_EXTENSION}")


@router.get("/404.png", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
async def _get_404():
    image = get_basic_404("Image could not be found on server")
    image = dithering.atkinson_dither(image)
    image_bytes = image_to_bytes(image)
    return Response(image_bytes, headers=IMAGE_HEADER, media_type=f"image/{IMAGE_EXTENSION}")
