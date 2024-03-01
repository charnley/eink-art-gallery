import os
import textwrap

import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
from matplotlib import patheffects, rcParams
from PIL import Image


class outline:
    def __init__(
        self,
    ):

        self._orig = rcParams.copy()
        rcParams.update(
            {
                "path.effects": [patheffects.withStroke(linewidth=5, foreground="w")],
                "lines.linewidth": 3.0,
                # scatter plot defaults
                "lines.markersize": 10,
            }
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        dict.update(rcParams, self._orig)


def display_images(
    images: list[Image.Image],
    num_cols=2,
    title=None,
):

    if not len(images):
        raise ValueError("No images")

    images = images[:4]

    num_images = len(images)
    num_cols = min(num_images, num_cols)
    num_rows = int(num_images / num_cols) + (1 if num_images % num_cols != 0 else 0)

    figure, axes = plt.subplots(num_rows, num_cols, figsize=(10, 10))

    axes = list(axes.flat)

    for i, (ax, image) in enumerate(zip(axes, images)):
        ax.imshow(image)
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.set_aspect("equal")

    for ax in axes[num_images:]:
        ax.set_visible(False)

    figure.subplots_adjust(wspace=0, hspace=0)
    figure.tight_layout()

    if title:
        txt = figure.suptitle(title, fontsize=11)
        txt.set_path_effects([PathEffects.withStroke(linewidth=5, foreground="w")])
