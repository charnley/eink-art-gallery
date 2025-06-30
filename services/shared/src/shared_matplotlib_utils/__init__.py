from datetime import datetime
from functools import lru_cache
from io import BytesIO
from typing import Any

import qrcode
from matplotlib import patheffects
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image
from PIL.Image import Image as PilImage
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


def plot_to_image(fig: Figure, dpi: int = IMAGE_DPI) -> PilImage:
    buf = BytesIO()
    fig.savefig(buf, dpi=dpi)
    buf.seek(0)
    img = Image.open(buf)
    return img


def close():
    plt.close()


def get_basic_text(
    text: str, alt_text: None = None, with_date: bool = True, font: dict[Any, Any] = FONT, width=IMAGE_WIDTH, height=IMAGE_HEIGHT,
) -> PilImage:

    now = datetime.now()

    (fig, ax) = get_figure(width=width, height=height)

    ax.text(
        0.5,
        0.55,
        text,
        verticalalignment="center",
        horizontalalignment="center",
        fontsize=18,
        wrap=True,
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

    close()

    return image


@lru_cache()
def get_basic_404(text, font=FONT, width=IMAGE_WIDTH, height=IMAGE_HEIGHT):

    (fig, ax) = get_figure(width=width, height=height)

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

    close()

    return image


def generate_wifi_qrcode(
    ssid: str,
    password: str,
    wifi_type="WPA",
) -> PilImage:
    wifi_data = f"WIFI:T:{wifi_type};S:{ssid};P:{password};;"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=4,
    )

    qr.add_data(wifi_data)
    qr.make(fit=True)

    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_image = qr_image.convert("RGBA")

    return qr_image


def get_basic_wifi(wifi_name, wifi_password, wifi_type="WPA", font=FONT) -> PilImage:

    (fig, ax) = get_figure()

    qr_image = generate_wifi_qrcode(wifi_name, wifi_password, wifi_type=wifi_type)

    imagebox = OffsetImage(qr_image, zoom=1.0)
    imagebox.image.axes = ax

    ab = AnnotationBbox(imagebox, (0.5, 0.5), xycoords="axes fraction", bboxprops={"lw": 0})

    ax.add_artist(ab)

    ax.axis("off")

    image = plot_to_image(fig)

    close()

    return image
