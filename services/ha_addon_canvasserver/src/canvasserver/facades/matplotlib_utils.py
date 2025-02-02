import io

from canvasserver.constants import IMAGE_DPI, IMAGE_HEIGHT, IMAGE_WIDTH
from matplotlib import pyplot as plt
from PIL import Image


def get_figure(width=IMAGE_WIDTH, height=IMAGE_HEIGHT, dpi=IMAGE_DPI):
    fig, ax = plt.subplots(1, 1, figsize=(width // dpi, height // dpi), dpi=dpi)
    return fig, ax


def plot_to_image(fig, dpi=IMAGE_DPI) -> Image.Image:
    buf = io.BytesIO()
    fig.savefig(buf, dpi=dpi)
    buf.seek(0)
    img = Image.open(buf)
    return img
