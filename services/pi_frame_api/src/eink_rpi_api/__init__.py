import logging
import warnings
from contextlib import asynccontextmanager
from io import BytesIO

from fastapi import FastAPI, HTTPException, UploadFile
from PIL import Image
from pydantic import BaseModel
from shared_constants import WaveshareDisplay
from shared_matplotlib_utils import get_basic_text

from . import displaying
from .config import get_settings

logger = logging.getLogger(__name__)

warnings.filterwarnings(
    "ignore", message="PinFactoryFallback: Falling back from lgpio: No module named 'lgpio'"
)


__version__ = "1.0.0"
__title__ = "EinkRaspberryPiAPI"


@asynccontextmanager
async def lifespan(_: FastAPI):

    logger.info("Loading settings...")
    settings = get_settings()

    epd_type = settings.EPD_TYPE
    assert isinstance(epd_type, WaveshareDisplay)
    displaying.EPD_TYPE = epd_type

    logger.info("Starting Picture API...")

    # clear on boot
    displaying.init()
    displaying.clear()

    image = get_basic_text("Ready", with_date=False, width=epd_type.width, height=epd_type.height)
    displaying.display(image)

    displaying.sleep()

    yield
    # clear on exit
    logger.info("Exiting Picture API")
    displaying.init()
    displaying.clear()
    displaying.sleep()


logger = logging.getLogger(__name__)
app = FastAPI(lifespan=lifespan, version=__version__, title=__title__)


@app.post("/display/image")
async def display_image(file: UploadFile):
    """Upload pillow supported image"""

    epd_type = displaying.EPD_TYPE

    filename = file.filename
    content_type = file.content_type

    logging.info(f"displaying {filename} of type {content_type} on {displaying.EPD_TYPE}")

    request_object_content = await file.read()
    image = Image.open(BytesIO(request_object_content))

    width, height = image.size

    if width != epd_type.width or height != epd_type.height:
        logger.error("Wrong size")
        raise HTTPException(status_code=400, detail=f"Bad input size '{width}x{height}'")

    displaying.init()
    displaying.display(image)
    displaying.sleep()


class TextPost(BaseModel):
    text: str = "Hello"
    include_date: bool = True


@app.post("/display/text")
async def display_text(body: TextPost):
    """Set the text of the display"""
    text = body.text
    with_date = body.include_date

    epd_type = displaying.EPD_TYPE

    if not len(text):
        logger.info("Not text to display, ignored.")
        return

    image = get_basic_text(text, with_date=with_date, height=epd_type.height, width=epd_type.width)

    displaying.init()
    displaying.display(image)
    displaying.sleep()


@app.post("/display/clear")
async def set_clear():
    """Reset the display"""
    displaying.init()
    displaying.clear()
    displaying.sleep()


@app.get("/status")
async def get_status():
    return {"status": "ready", "display_type": displaying.EPD_TYPE}
