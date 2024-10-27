import logging
from contextlib import asynccontextmanager
from io import BytesIO

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi_utilities import repeat_at
from PIL import Image

import picture_shower


@asynccontextmanager
async def lifespan(app: FastAPI):
    # clear on boot
    clear()
    yield
    # clear on exit
    clear()


logger = logging.getLogger(__name__)
app = FastAPI()

WIDTH = 960
HEIGHT = 680


@repeat_at(cron="0 3 * * *")  # every 3 am
def clear():
    logger.info("Repeat reset")
    picture_shower.init()
    picture_shower.clear()
    picture_shower.sleep()


@app.post("/display/bitmap")
async def display_bitmap(file: UploadFile):
    """Upload image/bmp"""

    filename = file.filename
    content_type = file.content_type

    if content_type != "image/bmp":
        raise HTTPException(status_code=400, detail=f"Bad input type '{content_type}'")

    logging.info(f"displaying {filename} of type {content_type}")

    request_object_content = await file.read()
    image = Image.open(BytesIO(request_object_content))
    width, height = image.size

    if width != WIDTH or height != HEIGHT:
        raise HTTPException(status_code=400, detail=f"Bad input size '{width}x{height}'")

    picture_shower.init()
    picture_shower.display(image)
    picture_shower.sleep()


@app.post("/display/image")
async def display_image(file: UploadFile):
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
    picture_shower.display(image)
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
