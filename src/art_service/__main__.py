import logging
import threading
import warnings
from io import BytesIO

import requests
from PIL import Image
from rich.logging import RichHandler

from art_generator import load_flux_schnell, load_sd3, prompt_flux_schnell, prompt_sd3
from art_utils import atkinson_dither, image_split_red_channel
from art_utils.network_utils import send_photo, send_photo_red

warnings.filterwarnings("ignore", category=UserWarning)
logger = logging.getLogger(__name__)

PUSH_URL = "http://192.168.1.26:8080"

QUEUE_URL = "http://localhost:8000"
ENDPOINT_CHECK = "/actions/queue_check"
ENDPOINT_UPLOAD = "/images"


# Default Image format
IMAGE_FORMAT = "PNG"
IMAGE_EXTENSION = "png"
IMAGE_CONTENT_TYPE = "image/png"
FILE_UPLOAD_KEY = "files"

# Default Image settings
IMAGE_DPI = 96
IMAGE_WIDTH = 960
IMAGE_HEIGHT = 680


def image_to_bytes(image: Image.Image):
    """Return bytes of image in default image format"""

    with BytesIO() as buf:
        image.save(buf, format=IMAGE_FORMAT)
        image_bytes = buf.getvalue()

    return image_bytes


def bytes_to_image(image_data) -> Image.Image:
    image = Image.open(BytesIO(image_data))
    return image


def request_task(url, params, files):
    response = requests.post(url, params=params, files=files)
    logger.info(f"Photo send and received: {response.status_code}")


def fire_and_forget(url, params, files):
    threading.Thread(target=request_task, args=(url, params, files)).start()


def refill(args):

    logger.info(f"Fetching from {args.canvas_server_url + ENDPOINT_CHECK}")
    response = requests.get(args.canvas_server_url + ENDPOINT_CHECK)

    assert response.status_code == 200, response.json()

    data = response.json()
    prompts = data["prompts"]

    logger.info(f"Got {len(prompts)} prompts need of refill...")

    # Nothing to do

    if data["count"] == 0:
        logger.info("Nothing todo... exiting")
        return

    # Load model
    load_func = load_sd3
    prompt_func = prompt_sd3

    pipe = load_func()

    for prompt in prompts:

        prompt_text = prompt["prompt"]
        prompt_id = prompt["id"]
        # prompt_model = prompt["model"]

        logger.info(f"Generating images for {prompt_id}...")

        # Generate images
        images = [prompt_func(pipe, prompt_text) for _ in range(args.canvas_server_fill_count)]

        files = [
            (FILE_UPLOAD_KEY, (f"file{i}", image_to_bytes(image), IMAGE_CONTENT_TYPE))
            for i, image in enumerate(images)
        ]

        logger.info(f"Uploading images for {prompt_id}...")
        params = dict(prompt=prompt_id)
        fire_and_forget(args.canvas_server_url + ENDPOINT_UPLOAD, params=params, files=files)


def push_picture(args):

    # Generate random prompt first
    if args.prompt is None:
        logger.info("Generating a random prompt")
        prompt = "ink drawing, man yelling, with sign saying 'prompt not found'"

    else:
        prompt = " ".join(args.prompt)

    logger.info(f"prompt: {prompt}")
    logger.info("Generating a random photo")

    if args.use_red:
        logger.info("Add some red")
        prompt = prompt.replace("bw", "bw and red")

    if args.method == "SD3":
        load_func = load_sd3
        prompt_func = prompt_sd3

    elif args.method == "FluxSchnell":
        load_func = load_flux_schnell
        prompt_func = prompt_flux_schnell

    assert load_func is not None
    assert prompt_func is not None

    # okay
    pipe = load_func()
    image = prompt_func(pipe, prompt)

    # Free GPU Mem
    del pipe

    # Dither

    if args.use_red:
        logger.info("splitting and dithering the picture")
        image_r, image_b = image_split_red_channel(image)
        image_r = atkinson_dither(image_r)
        image_b = atkinson_dither(image_b)
        logger.info("Sending it to red paper frame")
        r = send_photo_red(image_b, image_r, f"{PUSH_URL}/display/redImage")

    else:
        logger.info("dithering the picture")
        logger.info("Sending it to paper frame")
        image = atkinson_dither(image)
        r = send_photo(image, f"{PUSH_URL}/display/image")

    logger.info(f"Got {r} after {r.elapsed.total_seconds()} seconds")
    image.save("test.bmp")


def main(args=None):

    import argparse

    FORMAT = "%(message)s"
    logging.basicConfig(
        level=logging.INFO, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

    parser = argparse.ArgumentParser()

    parser.add_argument("--push", action="store_true")
    parser.add_argument("--prompt", type=str, default=None, nargs="+")
    parser.add_argument("--method", type=str, default="SD3", choices=["SD3", "FluxSchnell"])
    parser.add_argument("--use-red", action="store_true", default=False)

    parser.add_argument("--refill", action="store_true")
    parser.add_argument("--canvas-server-url", default=QUEUE_URL, type=str)
    parser.add_argument("--canvas-server-fill-count", type=int, default=2)

    args = parser.parse_args(args)

    if args.refill:
        refill(args)

    if args.push:
        push_picture(args)


if __name__ == "__main__":
    main()
