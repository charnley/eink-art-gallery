from datetime import datetime
from functools import cache

from ..constants import DATE_FORMAT, FONT_FAMILY, FONT_WEIGHT
from . import matplotlib_utils

FONT = dict(
    fontweight=FONT_WEIGHT,
    fontfamily=FONT_FAMILY,
)


def get_basic_text(text, alt_text=None, font=FONT):

    now = datetime.now()

    (fig, ax) = matplotlib_utils.get_figure()

    ax.text(
        0.5,
        0.55,
        text,
        verticalalignment="center",
        horizontalalignment="center",
        fontsize=22,
        **font,
    )

    ax.text(
        0.5,
        0.45,
        now.strftime(DATE_FORMAT),
        verticalalignment="center",
        horizontalalignment="center",
        fontsize=15,
        **font,
    )

    ax.axis("off")

    image = matplotlib_utils.plot_to_image(fig)

    return image


def get_basic_404(text, font=FONT):

    now = datetime.now()

    (fig, ax) = matplotlib_utils.get_figure()

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

    ax.text(
        0.5,
        0.30,
        now.strftime(DATE_FORMAT),
        verticalalignment="center",
        horizontalalignment="center",
        fontsize=15,
        **font,
    )

    ax.axis("off")

    image = matplotlib_utils.plot_to_image(fig)

    return image
