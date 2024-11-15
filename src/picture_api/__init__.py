import logging
from contextlib import asynccontextmanager
from io import BytesIO

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi_utilities import repeat_at
from PIL import Image

import picture_shower

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Picture API")
    # clear on boot
    clear()
    # TODO Create text on display
    yield
    # clear on exit
    logger.info("Exiting Picture API")
    clear()


logger = logging.getLogger(__name__)
app = FastAPI(lifespane=lifespan)

WIDTH = 960
HEIGHT = 680


@repeat_at(cron="0 3 * * *")  # every 3 am
def clear():
    logger.info("Repeat reset")
    picture_shower.init()
    picture_shower.clear()
    picture_shower.sleep()


@app.post("/display/image")
async def display_image(file: UploadFile, useGrey: bool = False):
    """Upload pillow supported image"""

    filename = file.filename
    content_type = file.content_type

    logging.info(f"displaying {filename} of type {content_type}")

    request_object_content = await file.read()
    image = Image.open(BytesIO(request_object_content))

    width, height = image.size

    if width != WIDTH or height != HEIGHT:
        raise HTTPException(status_code=400, detail=f"Bad input size '{width}x{height}'")

    picture_shower.init()
    picture_shower.display(image, use_grey=useGrey)
    picture_shower.sleep()


@app.post("/display/redImage")
async def display_red_image(redFile: UploadFile, blackFile: UploadFile):
    """Upload pillow supported images"""

    filename_red = redFile.filename
    filename_black = blackFile.filename

    request_object_content = await filename_red.read()
    image_red = Image.open(BytesIO(request_object_content))

    request_object_content = await filename_black.read()
    image_black = Image.open(BytesIO(request_object_content))

    if image_red.size != image_black.size:
        raise HTTPException(
            status_code=400, detail=f"Bad input size '{image_red.size}' and '{image_black.size}'"
        )

    width, height = image_red.size

    if width != WIDTH or height != HEIGHT:
        raise HTTPException(status_code=400, detail=f"Bad input size '{width}x{height}'")

    picture_shower.init()
    picture_shower.display_red(image_red, image_black)
    picture_shower.sleep()


@app.post("/display/text")
async def display_text():
    """Set the text of the display"""
    raise NotImplementedError()


@app.post("/display/clear")
async def set_clear():
    """Reset the display"""
    picture_shower.init()
    picture_shower.clear()
    picture_shower.sleep()


@app.get("/status")
async def get_status():
    # TODO Get if display is busy

    # Enums:
    # busy
    # ready

    return {"status": "ready"}
