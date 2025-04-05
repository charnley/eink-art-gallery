from io import BytesIO

from PIL import Image
from shared_constants import FILE_UPLOAD_KEY, IMAGE_CONTENT_TYPE, IMAGE_FORMAT


def image_to_bytes(image: Image.Image):
    """Return bytes of image in default image format"""

    with BytesIO() as buf:
        image.save(buf, format=IMAGE_FORMAT)
        image_bytes = buf.getvalue()

    return image_bytes


def bytes_to_image(image_data) -> Image.Image:
    image = Image.open(BytesIO(image_data))
    return image
