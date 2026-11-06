import logging
from datetime import timedelta

from desktop_server.canvas_client import (
    color_range_from_display,
    get_display_models,
    get_groups,
    post_prompts,
)
from desktop_server.generate_prompts import (
    DEFAULT_MODEL,
    generate_prompts_for_themes,
    ollama_session,
)

logger = logging.getLogger(__name__)


def _resolve_counts(
    canvas_server_url: str,
    count: int | None,
    time_period: timedelta | None,
) -> dict:
    """Return prompt count per display model, either fixed or computed from groups."""
    display_models = get_display_models(canvas_server_url)
    assert display_models, "No display models registered on the canvas coordinator"

    if count is not None:
        return {model: count for model in display_models}

    assert time_period is not None
    from desktop_server.refill.time_utils import compute_needed_prompts

    groups = get_groups(canvas_server_url)
    return compute_needed_prompts(groups, display_models, time_period)


def refill_prompts(
    theme: str,
    count: int | None,
    canvas_server_url: str,
    system_prompt: str,
    task_template: str,
    model: str = DEFAULT_MODEL,
    time_period: timedelta | None = None,
) -> None:
    """Generate prompts from a theme via Ollama, one batch per display model
    registered on the canvas coordinator, and post them back."""

    counts = _resolve_counts(canvas_server_url, count, time_period)
    display_models = list(counts.keys())

    logger.info(f"Found {len(display_models)} display model(s) registered:")
    for display_model in display_models:
        logger.info(f"  {display_model.value} -> {color_range_from_display(display_model)}")

    logger.info(f"Theme: {theme}")
    if time_period:
        logger.info(f"Time period: {time_period} using {model}")

    with ollama_session(model):
        for display_model in display_models:
            n = counts[display_model]
            color_range = color_range_from_display(display_model)

            logger.info(f"Generating {n} prompts for {display_model.value} ({color_range})...")

            if n <= 0:
                logger.info(f"Skipping {display_model.value}, no prompts needed")
                continue

            prompts = generate_prompts_for_themes(
                [theme],
                n,
                color_range=color_range,
                system_prompt=system_prompt,
                task_template=task_template,
                model=model,
            )

            post_prompts(
                prompts,
                display_model=display_model,
                server_url=canvas_server_url,
            )

    logger.info("Done")
