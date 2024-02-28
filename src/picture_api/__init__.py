import logging
from io import BytesIO

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi_utilities import repeat_at
from PIL import Image

import picture_shower

logger = logging.getLogger(__name__)
app = FastAPI()


@app.on_event("startup")
async def hey2():
    print("hey2")


@app.on_event("startup")
@repeat_at(cron="*/2 * * * *")  # every 2nd minute
async def hey():
    print("hey")


@app.on_event("startup")
@repeat_at(cron="0 3 * * *")  # every 3 am
def start_up():
    logger.info("Repeat reset")
    picture_shower.init()
    picture_shower.clear()
    picture_shower.sleep()


@app.post("/display/bitmap")
async def display_image(file: UploadFile):
    """Upload image/bmp"""

    filename = file.filename
    content_type = file.content_type

    if content_type != "image/bmp":
        raise HTTPException(status_code=400, detail=f"Bad input type '{content_type}'")

    logging.info(f"displaying {filename} of type {content_type}")

    request_object_content = await file.read()
    image = Image.open(BytesIO(request_object_content))

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
