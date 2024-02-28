import logging
from io import BytesIO
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image

import picture_shower

logger = logging.getLogger(__name__)
app = FastAPI()

# @app.post("/files/")
# async def create_file(file: Annotated[bytes, File()]):
#     return {"file_size": len(file)}


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

    return {"filename": file.filename}


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
    raise NotImplementedError()


@app.get("/status")
async def get_status():
    # TODO Get if display is busy

    # Enums:
    # busy
    # ready

    return {"status": "ready"}
