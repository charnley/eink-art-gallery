
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import textwrap, os
from matplotlib import patheffects, rcParams, ticker
import matplotlib.patheffects as PathEffects


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
    # columns=2, width=2, height=8,
    # label_wrap_length=50, label_font_size=8
    title=None,
):

    if not len(images):
        raise ValueError("No images")

    images = images[:4]

    num_images = len(images)
    num_cols = min(num_images, num_cols)
    num_rows = int(num_images / num_cols) + (1 if num_images % num_cols != 0 else 0)

    figure, axes = plt.subplots(num_rows, num_cols, figsize=(10,10))

    axes = list(axes.flat)

    for i, (ax, image) in enumerate(zip(axes, images)):
        ax.imshow(image)
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_aspect('equal')

    for ax in axes[num_images:]:
        ax.set_visible(False)

    figure.subplots_adjust(wspace=0, hspace=0)
    figure.tight_layout()

    if title:
        # effect = patheffects.withStroke(linewidth=5, foreground="w")
        # fontproperties = dict()
        # fontproperties["path.effects"] = effect

        txt = figure.suptitle(title, fontsize=11)
        txt.set_path_effects([PathEffects.withStroke(linewidth=5, foreground='w')])

    return




    height = total_rows
    width = 10


    height = max(height, int(len(images)/columns) * height)
    plt.figure(figsize=(width, height))

    for i, image in enumerate(images):

        plt.subplot(int(len(images) / columns + 1), columns, i + 1)
        plt.imshow(image)

        if hasattr(image, 'filename'):
            title=image.filename
            if title.endswith("/"): title = title[0:-1]
            title=os.path.basename(title)
            title=textwrap.wrap(title, label_wrap_length)
            title="\n".join(title)
            plt.title(title, fontsize=label_font_size); 


