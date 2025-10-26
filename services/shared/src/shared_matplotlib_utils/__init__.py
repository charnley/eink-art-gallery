import textwrap
from datetime import datetime
from functools import lru_cache
from io import BytesIO
from typing import Any

import qrcode
from matplotlib import patheffects
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.textpath import TextPath
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

TEXT_LENGTH = 30


def calculate_fontsize(fig, ax, font=FONT) -> int:

    target_width_pct = 0.8
    font_base = 15
    test_text = "A" * TEXT_LENGTH

    text_obj = ax.text(
        0.5,
        0.5,
        test_text,
        verticalalignment="center",
        horizontalalignment="center",
        fontsize=font_base,
        **font,
    )

    fig.canvas.draw()
    text_width = text_obj.get_window_extent(renderer=fig.canvas.get_renderer()).width
    ax_width_px = ax.get_window_extent().width

    target_width_px = ax_width_px * target_width_pct
    penalty = target_width_px / text_width
    font_size = int(font_base * penalty)

    text_obj.remove()

    return font_size


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
    text: str,
    alt_text: None = None,
    with_date: bool = True,
    font: dict[Any, Any] = FONT,
    width=IMAGE_WIDTH,
    height=IMAGE_HEIGHT,
) -> PilImage:

    now = datetime.now()

    (fig, ax) = get_figure(width=width, height=height)

    font_size = calculate_fontsize(fig, ax, font=font)
    text = textwrap.wrap(text, width=TEXT_LENGTH)
    font_size_text = font_size * (TEXT_LENGTH / len(text[0]))

    ax.text(
        0.5,
        0.55,
        "\n".join(text),
        verticalalignment="center",
        horizontalalignment="center",
        fontsize=font_size_text,
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
            bbox=dict(facecolor="black"),
            color="white",
            fontsize=font_size - 5,
            **FONT_MONO,
        )

    ax.axis("off")

    image = plot_to_image(fig)

    close()

    return image


@lru_cache()
def get_basic_404(reason, font=FONT, width=IMAGE_WIDTH, height=IMAGE_HEIGHT):

    (fig, ax) = get_figure(width=width, height=height)

    text_404 = "404"

    font_size = calculate_fontsize(fig, ax, font=font)
    reason = "\n".join(textwrap.wrap(reason, width=TEXT_LENGTH))
    # reason_size_text = font_size * (TEXT_LENGTH / (len(reason) + 1)) * 0.8
    font_size_404 = font_size * (TEXT_LENGTH / (len(text_404) + 1)) * 0.8

    ax.text(
        0.5,
        0.55,
        text_404,
        verticalalignment="center",
        horizontalalignment="center",
        fontsize=font_size_404,
        **font,
    )

    ax.text(
        1.0,
        0,
        reason,
        verticalalignment="center",
        horizontalalignment="right",
        bbox=dict(facecolor="black"),
        color="white",
        fontsize=font_size - 5,
        **FONT_MONO,
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


def get_basic_wifi(
    wifi_name, wifi_password, wifi_type="WPA", font=FONT, width=IMAGE_WIDTH, height=IMAGE_HEIGHT
) -> PilImage:

    (fig, ax) = get_figure(width=width, height=height)

    qr_image = generate_wifi_qrcode(wifi_name, wifi_password, wifi_type=wifi_type)

    imagebox = OffsetImage(qr_image, zoom=1.0)
    imagebox.image.axes = ax

    ab = AnnotationBbox(imagebox, (0.5, 0.5), xycoords="axes fraction", bboxprops={"lw": 0})

    ax.add_artist(ab)

    ax.axis("off")

    image = plot_to_image(fig)

    close()

    return image
