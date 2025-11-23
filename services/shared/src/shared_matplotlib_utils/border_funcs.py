import numpy as np


def fix_borders(ax, visibles=[False, False, True, True], fix_bounds=True):
    """Make border pretty"""

    # TODO What if xticks are not numeric? like categories

    directions = ["top", "right", "bottom", "left"]

    spines = ax.spines.items()
    spines = dict(spines)

    xticks = ax.get_xticks()
    yticks = ax.get_yticks()
    min_x, max_x = ax.get_xlim()
    min_y, max_y = ax.get_ylim()

    # Correct to the actual ticks
    (x_idxs,) = np.where((xticks >= min_x) & (xticks <= max_x))
    (y_idxs,) = np.where((yticks >= min_y) & (yticks <= max_y))
    xticks = xticks[x_idxs]
    yticks = yticks[y_idxs]

    xticks = list(xticks)
    yticks = list(yticks)

    if xticks:
        min_x = np.min(xticks)
        max_x = np.max(xticks)

    if yticks:
        min_y = np.min(yticks)
        max_y = np.max(yticks)

    # TODO Better ax.set_xlim()

    for direction, visible in zip(directions, visibles):

        spine = spines[direction]
        spine.set_visible(visible)

        if not visible and direction == "left":
            ax.yaxis.set_visible(False)

        if not visible:
            continue

        if not fix_bounds:
            continue

        if direction == "left" or direction == "right":
            if yticks:
                spine.set_bounds(min_y, max_y)

        else:
            if xticks:
                spine.set_bounds(min_x, max_x)
