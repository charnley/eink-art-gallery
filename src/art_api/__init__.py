# TODO Service that HomeAssistant can call to generate art with prompt

import logging
import random
import time
from functools import cache
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi_utilities import repeat_at, repeat_every
from PIL import Image
from pydantic import BaseModel

from art_generator import load_sd3, prompt_sd3
from art_utils import atkinson_dither
from art_utils.network_utils import send_photo

logger = logging.getLogger(__name__)
app = FastAPI()

HERE = Path.cwd()

config = {"picture_api": "http://192.168.1.26:8080/display/bitmap"}


def get_ttl_hash(seconds=3600):
    """Return the same value withing `seconds` time period"""
    return round(time.time() / seconds)


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

    pipe = load_sd3()
    image = prompt_sd3(pipe, str(promptPost.prompt))

    # Dither
    logger.info("dithering the picture")
    image = atkinson_dither(image)

    logger.info("Sending it to paper frame")
    send_photo(image, config["picture_api"])

    # Free GPU Mem
    del pipe

    return {}


# @cache
def generate_random(ttl_hash=None):

    filename = Path(__file__) / "../../../assets/random_artists.txt"
    filename = filename.resolve()

    with open(filename) as f:
        lines = f.read().splitlines()
        prompt = random.choice(lines).strip()

    logger.info("Generating random photo")

    pipe = load_sd3()
    image = prompt_sd3(pipe, str(prompt))

    # Dither
    logger.info("dithering the picture")
    image = atkinson_dither(image)

    # Cache hack
    image.save(HERE / "cache.png")

    return image


@app.get("/cache.png", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
async def _fetch_cache():

    image = Image.open(HERE / "cache.png")
    logger.info(f"Loading cache from {HERE}")

    with BytesIO() as buf:
        image.save(buf, format="png")
        image_bytes = buf.getvalue()

    headers = {"Content-Disposition": 'inline; filename="image.png"'}
    return Response(image_bytes, headers=headers, media_type="image/png")


@app.on_event("startup")
@repeat_at(cron="0 */5 * * *")
def _generate_random():
    ttl_hash = get_ttl_hash()
    logger.info(f"Generating random with ttl {ttl_hash}")
    image = generate_random(ttl_hash=ttl_hash)
    return image


@app.get("/image.png", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
def get_image():

    filename = Path.cwd() / "images/960x680/test.png"
    image = Image.open(filename)

    with BytesIO() as buf:
        image.save(buf, format="png")
        image_bytes = buf.getvalue()

    headers = {"Content-Disposition": 'inline; filename="image.png"'}

    return Response(image_bytes, headers=headers, media_type="image/png")


@app.get("/test.png", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
def get_test_image():

    filename = Path.cwd() / "images/960x680/test.png"
    image = Image.open(filename)

    with BytesIO() as buf:
        image.save(buf, format="png")
        image_bytes = buf.getvalue()

    headers = {"Content-Disposition": 'inline; filename="test.png"'}

    return Response(image_bytes, headers=headers, media_type="image/png")
