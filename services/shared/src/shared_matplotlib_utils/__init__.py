import textwrap
import unicodedata
from datetime import datetime
from io import BytesIO
from typing import Any

import numpy as np
import qrcode
from matplotlib import patheffects
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image
from PIL.Image import Image as PilImage
from shared_constants import (
    DATE_FORMAT_SHORT,
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

OUTLINE = patheffects.withStroke(linewidth=4, foreground="w")

BBOX = bbox = dict(
    pad=2,
    facecolor="black",
)

TEXT_LENGTH = 30


def visual_length(text: str) -> float:
    """Estimate the visual width of text based on Unicode categories."""
    length = 0.0
    for ch in text:
        if ch.isspace():
            length += 0.5
        else:
            ea = unicodedata.east_asian_width(ch)
            # Wide or fullwidth chars (Hangul, Kanji, Emoji)
            if ea in ("W", "F"):
                length += 1.8
            else:
                length += 1.0

    return length


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


def close(fig=None):
    if fig is None:
        plt.close()
        return
    plt.close(fig)


def get_basic_text(
    text: str,
    with_date: bool = True,
    font: dict[Any, Any] = FONT,
    width=IMAGE_WIDTH,
    height=IMAGE_HEIGHT,
    split_on_dot=True,
) -> PilImage:

    now = datetime.now()

    (fig, ax) = get_figure(width=width, height=height)

    if split_on_dot:
        text = ".\n".join([t.strip() for t in text.split(".")])
        text = text.strip()

    line_lengths = [visual_length(line) for line in text.splitlines()]
    line_length = max(max(line_lengths), 1)

    aspect = width / height

    base_size = 200  # Empirically choosen
    font_size = max(8, base_size * np.sqrt(aspect) / np.sqrt(line_length))

    ax.text(
        0.5,
        0.5,
        text,
        verticalalignment="center",
        horizontalalignment="center",
        fontsize=font_size,
        wrap=True,
        **font,
    )

    if with_date:

        subtext = now.strftime(DATE_FORMAT_SHORT)
        subbasefont = 35
        subfontsize = max(8, subbasefont * np.sqrt(aspect) / np.sqrt(len(subtext)))

        ax.text(
            1.0,
            0,
            now.strftime(DATE_FORMAT_SHORT),
            verticalalignment="center",
            horizontalalignment="right",
            bbox=BBOX,
            color="white",
            fontsize=subfontsize,
            **FONT_MONO,
        )

    ax.axis("off")

    image = plot_to_image(fig)

    close(fig)

    return image


def get_basic_404(reason, font=FONT, width=IMAGE_WIDTH, height=IMAGE_HEIGHT):

    (fig, ax) = get_figure(width=width, height=height)

    text_404 = "404"

    if reason is None:
        now = datetime.now()
        reason = now.strftime(DATE_FORMAT_SHORT)

    aspect = width / height

    base_size = 200  # Empirically choosen
    font_size = max(8, base_size * np.sqrt(aspect) / np.sqrt(4))

    ax.text(
        0.5,
        0.55,
        text_404,
        verticalalignment="center",
        horizontalalignment="center",
        fontsize=font_size,
        **FONT_MONO,
    )

    reason = ".\n".join([t.strip() for t in reason.split(".")])
    reason = reason.strip()
    reason_base_size = 35

    reason_font_size = max(8, reason_base_size * np.sqrt(aspect) / np.sqrt(10))

    ax.text(
        1.0,
        0,
        reason,
        verticalalignment="bottom",
        horizontalalignment="right",
        bbox=BBOX,
        color="white",
        fontsize=reason_font_size,
        **FONT_MONO,
    )

    ax.axis("off")

    image = plot_to_image(fig)

    close(fig)

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


def get_basic_wifi(
    wifi_name, wifi_password, wifi_type="WPA", width=IMAGE_WIDTH, height=IMAGE_HEIGHT
) -> PilImage:

    (fig, ax) = get_figure(width=width, height=height)

    qr_image = generate_wifi_qrcode(wifi_name, wifi_password, wifi_type=wifi_type)

    imagebox = OffsetImage(qr_image, zoom=1.0)
    imagebox.image.axes = ax

    ab = AnnotationBbox(imagebox, (0.5, 0.5), xycoords="axes fraction", bboxprops={"lw": 0})

    ax.add_artist(ab)

    ax.axis("off")

    image = plot_to_image(fig)

    close(fig)

    return image
