from datetime import datetime
from functools import lru_cache
from io import BytesIO
from typing import Any

from matplotlib import patheffects
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from PIL import Image
from shared_constants import (
    DATE_FORMAT,
    FONT_FAMILY,
    FONT_FAMILY_MONO,
    FONT_WEIGHT,
    IMAGE_DPI,
    IMAGE_HEIGHT,
    IMAGE_WIDTH,
)

FONT = dict(
    fontweight=FONT_WEIGHT,
    fontfamily=FONT_FAMILY,
)

FONT_MONO = dict(
    fontweight=FONT_WEIGHT,
    fontfamily=FONT_FAMILY_MONO,
)

# path_effects=[OUTLINE]
OUTLINE = patheffects.withStroke(linewidth=4, foreground="w")


def get_figure(
    width: int = IMAGE_WIDTH, height: int = IMAGE_HEIGHT, dpi: int = IMAGE_DPI
) -> tuple[Figure, Axes]:
    fig, ax = plt.subplots(1, 1, figsize=(width / dpi, height / dpi), dpi=dpi)
    return fig, ax


def plot_to_image(fig: Figure, dpi: int = IMAGE_DPI) -> Image.Image:
    buf = BytesIO()
    fig.savefig(buf, dpi=dpi)
    buf.seek(0)
    img = Image.open(buf)
    return img


def get_basic_text(
    text: str, alt_text: None = None, with_date: bool = True, font: dict[Any, Any] = FONT
) -> Image.Image:

    now = datetime.now()

    (fig, ax) = get_figure()

    ax.text(
        0.5,
        0.55,
        text,
        verticalalignment="center",
        horizontalalignment="center",
        fontsize=22,
        **font,
    )

    if with_date:
        ax.text(
            1.0,
            0,
            now.strftime(DATE_FORMAT),
            verticalalignment="center",
            horizontalalignment="right",
            fontsize=14,
            bbox=dict(facecolor="black"),
            color="white",
            **FONT_MONO,
        )

    ax.axis("off")

    image = plot_to_image(fig)

    return image


@lru_cache()
def get_basic_404(text, font=FONT):

    (fig, ax) = get_figure()

    ax.text(
        0.5,
        0.55,
        "404",
        verticalalignment="center",
        horizontalalignment="center",
        fontsize=50,
        **font,
    )

    ax.text(
        0.5,
        0.40,
        text,
        verticalalignment="center",
        horizontalalignment="center",
        fontsize=15,
        **font,
    )

    ax.axis("off")

    image = plot_to_image(fig)

    return image
