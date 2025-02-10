import io
from typing import Tuple

from canvasserver.constants import IMAGE_DPI, IMAGE_HEIGHT, IMAGE_WIDTH
from matplotlib import pyplot as plt
from matplotlib.axes._axes import Axes
from matplotlib.figure import Figure
from PIL import Image


def get_figure(
    width: int = IMAGE_WIDTH, height: int = IMAGE_HEIGHT, dpi: int = IMAGE_DPI
) -> Tuple[Figure, Axes]:
    fig, ax = plt.subplots(1, 1, figsize=(width // dpi, height // dpi), dpi=dpi)
    return fig, ax


def plot_to_image(fig: Figure, dpi: int = IMAGE_DPI) -> Image.Image:
    buf = io.BytesIO()
    fig.savefig(buf, dpi=dpi)
    buf.seek(0)
    img = Image.open(buf)
    return img
