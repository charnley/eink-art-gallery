# TODO Service that HomeAssistant can call to generate art with prompt
# 192.168.1.24
import logging

from fastapi import FastAPI, HTTPException, UploadFile
from PIL import Image
from pydantic import BaseModel

from art_generator import (
    get_picture_fast,
    get_picture_slow,
    preload_fast_model,
    preload_slow_model,
    preload_slow_model3,
)
from art_utils import atkinson_dither
from art_utils.network_utils import send_photo

logger = logging.getLogger(__name__)
app = FastAPI()


class PromptPost(BaseModel):
    prompt: str


@app.on_event("startup")
def start_up():
    pass


@app.get("/status")
async def get_status():
    # TODO Get if display is busy

    # Enums:
    # busy
    # ready

    return {"status": "ready for prompts"}


@app.post("/prompt")
async def post_prompt(promptPost: PromptPost):

    logger.info(f"Prompt: {promptPost}")

    pipe = preload_slow_model3()
    image = get_picture_slow(pipe, str(promptPost.prompt))

    # Dither
    logger.info("dithering the picture")
    image = atkinson_dither(image)

    logger.info("Sending it to paper frame")
    send_photo(image, "http://192.168.1.26:8080/display/bitmap")

    # Free GPU Mem
    del pipe

    return {}
