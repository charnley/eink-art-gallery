import logging
import random
import time
import uuid
from functools import cache
from io import BytesIO
from pathlib import Path

from desktop_server.art_generator import load_sd3, prompt_sd3
from desktop_server.network_utils import send_photo, send_photo_red
from fastapi import BackgroundTasks, FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi_utilities import repeat_at, repeat_every
from PIL import Image
from pydantic import BaseModel
from shared_image_utils.dithering import atkinson_dither, image_split_red_channel

logger = logging.getLogger(__name__)
app = FastAPI()

HERE = Path.cwd()
QUEUE_DIR = (HERE / "../../queue/").resolve()

# TODO Should be options.json or settings
config = {"URL": "http://192.168.1.26:8080"}


def get_ttl_hash(seconds=3600):
    """Return the same value withing `seconds` time period"""
    return round(time.time() / seconds)


class PromptPost(BaseModel):
    prompt: str


@cache
def get_random_lines():

    # TODO Should be parameter
    filename = Path(__file__) / "../../../../../assets/random_artists.txt"
    filename = filename.resolve()

    with open(filename) as f:
        lines = f.read().splitlines()

    return lines


def get_random_line():
    lines = get_random_lines()
    return random.choice(lines).strip()


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

    prompt = str(promptPost.prompt)
    if prompt == "string" or prompt == "" or prompt is None or prompt == ",":
        logger.info("actually, use a random prompt")
        prompt = get_random_line()
        logger.info(prompt)

    pipe = load_sd3()
    image = prompt_sd3(pipe, prompt)

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

    logger.info(f"Got {r} after {r.elapsed.total_seconds():.0f} seconds")

    # Free GPU Mem
    # del pipe # TODO Keep-Alive mode

    return {}


@repeat_at(cron="*/5 * * * *")
def _generate_random_queue():
    logger.info("Checking for queue")
    filenames = list(dir.glob("**/*.png"))

    if not len(filenames):
        logger.info("Generating more images for the queue")
        generate_queue("", n_images=10)


def generate_queue(prompt, n_images=1):

    dir = QUEUE_DIR

    logger.info(f"Prompt: {prompt}")

    pipe = load_sd3()

    for _ in range(n_images):

        if prompt == "string" or prompt == "" or prompt is None:
            _prompt = get_random_line()
            logger.info("Use random prompt")
        else:
            _prompt = prompt

        image = prompt_sd3(pipe, _prompt)
        id = str(uuid.uuid4())

        filename = (dir / id).with_suffix(".png")
        image.save(filename, format="png")

    # Free GPU Mem
    del pipe

    return


@app.post("/images/generate")
async def post_prompt_queue(promptPost: PromptPost, nImages: int = 1):

    n_images = int(nImages)
    prompt = str(promptPost.prompt)
    generate_queue(prompt, n_images=n_images)

    return


# @cache
def generate_random(ttl_hash=None):

    # TODO get from settings
    filename = Path(__file__) / "../../../../../assets/random_artists.txt"
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

    logger.info(f"Loading cache from {HERE}")
    image = Image.open(HERE / "cache.png")

    with BytesIO() as buf:
        image.save(buf, format="png")
        image_bytes = buf.getvalue()

    headers = {"Content-Disposition": 'inline; filename="image.png"'}
    return Response(image_bytes, headers=headers, media_type="image/png")


@app.get("/queue.png", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
async def _fetch_queue():

    dir = QUEUE_DIR

    logger.info(f"Loading random from {dir}")

    filenames = list(dir.glob("**/*.png"))

    logger.info(f"Found {len(filenames)} random images")

    if not len(filenames):
        return None, 404

    filename = random.choice(filenames)

    image = Image.open(filename)
    image = atkinson_dither(image)

    filename.unlink()  # Delete

    with BytesIO() as buf:
        image.save(buf, format="png")
        image_bytes = buf.getvalue()

    headers = {"Content-Disposition": 'inline; filename="image.png"'}
    return Response(image_bytes, headers=headers, media_type="image/png")


# @app.on_event("startup")
# @repeat_at(cron="0 */5 * * *")
# def _generate_random():
#     ttl_hash = get_ttl_hash()
#     logger.info(f"Generating random with ttl {ttl_hash}")
#     image = generate_random(ttl_hash=ttl_hash)
#     return image


# @app.get("/image.png", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
# def get_image():

#     filename = Path.cwd() / "images/960x680/test.png"
#     image = Image.open(filename)

#     with BytesIO() as buf:
#         image.save(buf, format="png")
#         image_bytes = buf.getvalue()

#     headers = {"Content-Disposition": 'inline; filename="image.png"'}

#     return Response(image_bytes, headers=headers, media_type="image/png")


# @app.get("/test.png", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
# def get_test_image():

#     filename = Path.cwd() / "images/960x680/test.png"
#     image = Image.open(filename)

#     with BytesIO() as buf:
#         image.save(buf, format="png")
#         image_bytes = buf.getvalue()

#     headers = {"Content-Disposition": 'inline; filename="test.png"'}

#     return Response(image_bytes, headers=headers, media_type="image/png")
