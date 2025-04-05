import logging
import warnings
from contextlib import asynccontextmanager
from io import BytesIO

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi_utilities import repeat_at
from PIL import Image
from pydantic import BaseModel
from shared_constants import IMAGE_HEIGHT, IMAGE_WIDTH
from shared_matplotlib_utils import get_basic_text

from . import displaying

logger = logging.getLogger(__name__)

warnings.filterwarnings(
    "ignore", message="PinFactoryFallback: Falling back from lgpio: No module named 'lgpio'"
)

# TODO Move e-ink supported color and width and height to settings

__version__ = "x.y.z"
title = "EinkRaspberryPiAPI"


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting Picture API")
    # clear on boot
    displaying.init()
    displaying.clear()
    displaying.sleep()
    # TODO Create text on display

    yield
    # clear on exit
    logger.info("Exiting Picture API")
    displaying.init()
    displaying.clear()
    displaying.sleep()


logger = logging.getLogger(__name__)
app = FastAPI(lifespan=lifespan, version=__version__, title=title)


@app.post("/display/image")
async def display_image(file: UploadFile, useGrey: bool = False):
    """Upload pillow supported image"""

    filename = file.filename
    content_type = file.content_type

    logging.info(f"displaying {filename} of type {content_type}")

    request_object_content = await file.read()
    image = Image.open(BytesIO(request_object_content))

    width, height = image.size

    if width != IMAGE_WIDTH or height != IMAGE_HEIGHT:
        logger.error("Wrong size")
        raise HTTPException(status_code=400, detail=f"Bad input size '{width}x{height}'")

    displaying.init()
    displaying.display(image, use_grey=useGrey)
    displaying.sleep()


@app.post("/display/redImage")
async def display_red_image(redFile: UploadFile, blackFile: UploadFile):
    """Upload pillow supported images"""

    request_object_content = await redFile.read()
    image_red = Image.open(BytesIO(request_object_content))

    request_object_content = await blackFile.read()
    image_black = Image.open(BytesIO(request_object_content))

    if image_red.size != image_black.size:
        raise HTTPException(
            status_code=400, detail=f"Bad input size '{image_red.size}' and '{image_black.size}'"
        )

    width, height = image_red.size

    if width != IMAGE_WIDTH or height != IMAGE_HEIGHT:
        logger.error("Wrong size")
        raise HTTPException(status_code=400, detail=f"Bad input size '{width}x{height}'")

    displaying.init()
    displaying.display_red(image_red, image_black)
    displaying.sleep()


class TextPost(BaseModel):
    text: str = "Hello"
    include_date: bool = True


@app.post("/display/text")
async def display_text(body: TextPost):
    """Set the text of the display"""
    text = body.text
    with_date = body.include_date

    if not len(text):
        logger.info("Not text to display, ignored.")
        return

    image_red = get_basic_text(text, with_date=with_date)
    image_black = get_basic_text("", with_date=False)
    displaying.init()
    displaying.display_red(image_red, image_black)
    displaying.sleep()


@app.post("/display/clear")
async def set_clear():
    """Reset the display"""
    displaying.init()
    displaying.clear()
    displaying.sleep()


@app.get("/status")
async def get_status():
    return {"status": "ready"}
