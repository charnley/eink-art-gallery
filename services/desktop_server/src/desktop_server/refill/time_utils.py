import logging
from datetime import datetime, timedelta

from apscheduler.triggers.cron import CronTrigger
from shared_constants import WaveshareDisplay

logger = logging.getLogger(__name__)


def parse_time_period(time_str: str) -> timedelta:
    """Parse human-readable time strings like '1 week', '3 days', '2 hours'."""
    parts = time_str.strip().lower().split()
    if len(parts) != 2:
        raise ValueError(f"Expected '<number> <unit>', got '{time_str}'")

    try:
        value = int(parts[0])
    except ValueError:
        raise ValueError(f"Expected a number, got '{parts[0]}'")

    unit = parts[1].rstrip("s")
    mapping = {
        "hour": timedelta(hours=1),
        "day": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": timedelta(days=30),
        "year": timedelta(days=365),
    }

    if unit not in mapping:
        raise ValueError(f"Unknown time unit '{unit}'. Expected one of: {list(mapping.keys())}")

    return value * mapping[unit]


def count_cron_occurrences(cron_str: str, period: timedelta, start: datetime | None = None) -> int:
    """Count how many times a cron expression fires within a time period."""
    if not cron_str:
        return 0

    trigger = CronTrigger.from_crontab(cron_str)

    if start is None:
        start = datetime.now()
    end = start + period

    count = 0
    next_time = trigger.get_next_fire_time(start, start)

    while next_time and next_time <= end:
        count += 1
        next_time = trigger.get_next_fire_time(next_time, next_time)

    return count


def compute_needed_prompts(
    groups_info: list[dict],
    display_models: list[WaveshareDisplay],
    period: timedelta,
) -> dict[WaveshareDisplay, int]:
    """
    Calculate how many prompts per display model are needed to cover a time period.

    For each group we look at its frame refresh cron (schedule_frame) and prompt
    rotation cron (schedule_prompt).

    Total images needed  = Σ group_refreshes × frames_of_model_in_group
    Total prompts needed = max(ceil(images_needed / global_frame_count), rotations)

    Each prompt is seeded with enough images for the global frame count of its model,
    but prompt rotation requires at least one *unused* prompt per cycle.
    """
    total_images: dict[WaveshareDisplay, int] = {m: 0 for m in display_models}
    total_rotations: dict[WaveshareDisplay, int] = {m: 0 for m in display_models}
    global_frame_counts: dict[WaveshareDisplay, int] = {m: 0 for m in display_models}

    for group in groups_info:
        cron_frame = group.get("schedule_frame")
        cron_prompt = group.get("schedule_prompt")
        frames = group.get("frames", [])

        frame_events = count_cron_occurrences(cron_frame, period) if cron_frame else 0
        prompt_events = count_cron_occurrences(cron_prompt, period) if cron_prompt else 0

        # Count frames per model inside this group
        group_model_counts: dict[WaveshareDisplay, int] = {}
        for frame in frames:
            model = WaveshareDisplay(frame["model"])
            group_model_counts[model] = group_model_counts.get(model, 0) + 1
            global_frame_counts[model] = global_frame_counts.get(model, 0) + 1

        for model, n_frames in group_model_counts.items():
            total_images[model] += frame_events * n_frames
            total_rotations[model] += prompt_events

    result: dict[WaveshareDisplay, int] = {}
    for model in display_models:
        images_needed = total_images.get(model, 0)
        rotations_needed = total_rotations.get(model, 0)
        global_count = global_frame_counts.get(model, 0)

        if global_count == 0:
            result[model] = 0
            continue

        prompts_from_images = (images_needed + global_count - 1) // global_count  # ceil
        prompts_needed = max(prompts_from_images, rotations_needed)
        result[model] = prompts_needed

        logger.info(
            f"{model.value}: images_needed={images_needed}, "
            f"rotations_needed={rotations_needed}, frames_global={global_count} -> "
            f"{prompts_needed} prompts"
        )

    return result
