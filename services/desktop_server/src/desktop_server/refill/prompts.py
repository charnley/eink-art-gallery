import logging

from desktop_server.canvas_client import color_range_from_display, get_display_models, post_prompts
from desktop_server.generate_prompts import (
    DEFAULT_MODEL,
    generate_prompts_for_themes,
    ollama_session,
)

logger = logging.getLogger(__name__)


def refill_prompts(
    theme: str,
    count: int,
    canvas_server_url: str,
    system_prompt: str,
    task_template: str,
    model: str = DEFAULT_MODEL,
) -> None:
    """Generate prompts from a theme via Ollama, one batch per display model
    registered on the canvas coordinator, and post them back."""

    display_models = get_display_models(canvas_server_url)

    assert display_models, "No display models registered on the canvas coordinator"

    logger.info(f"Found {len(display_models)} display model(s) registered:")
    for display_model in display_models:
        logger.info(f"  {display_model.value} -> {color_range_from_display(display_model)}")

    logger.info(f"Theme: {theme}")
    logger.info(f"Generating {count} prompts per display model using {model}")

    with ollama_session(model):
        for display_model in display_models:
            color_range = color_range_from_display(display_model)

            logger.info(f"Generating for {display_model.value} ({color_range})...")

            prompts = generate_prompts_for_themes(
                [theme],
                count,
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
