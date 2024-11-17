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
from art_utils import atkinson_dither, image_split_red_channel
from art_utils.network_utils import send_photo, send_photo_red

logger = logging.getLogger(__name__)
app = FastAPI()

HERE = Path.cwd()

config = {"URL": "http://192.168.1.26:8080"}


def get_ttl_hash(seconds=3600):
    """Return the same value withing `seconds` time period"""
    return round(time.time() / seconds)


class PromptPost(BaseModel):
    prompt: str


@app.get("/status")
async def get_status():
    # TODO Get if display is busy

    # Enums:
    # busy
    # ready

    return {"status": "ready for prompts"}


@app.post("/prompt")
async def post_prompt(promptPost: PromptPost, useRed=True):

    logger.info(f"Prompt: {promptPost}")

    pipe = load_sd3()
    image = prompt_sd3(pipe, str(promptPost.prompt))

    if useRed:
        logger.info("splitting and dithering the picture")
        image_r, image_b = image_split_red_channel(image)
        image_r = atkinson_dither(image_r)
        image_b = atkinson_dither(image_b)
        logger.info("Sending it to red paper frame")
        r = send_photo_red(image_b, image_r, f"{config['URL']}/display/redImage")

    else:
        logger.info("dithering the picture")
        image = atkinson_dither(image)
        logger.info("Sending it to paper frame")
        r = send_photo(image, f"{config['URL']}/display/image")

    logger.info(f"Got {r} after {r.elapsed.total_seconds()} seconds")

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


@app.get("/refresh_cache")
async def generate_cache():
    ttl_hash = get_ttl_hash()
    logger.info(f"Generating random with ttl {ttl_hash}")
    generate_random(ttl_hash=ttl_hash)  # saves cache
    return {}, 200


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
