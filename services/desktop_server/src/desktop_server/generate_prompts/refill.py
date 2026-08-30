import logging
from pathlib import Path

from desktop_server.canvas_client import color_range_from_display, get_display_models, post_prompts
from desktop_server.generate_prompts import (
    DEFAULT_MODEL,
    generate_prompts_for_themes,
    ollama_session,
)
from rich.console import Console
from rich.logging import RichHandler

logger = logging.getLogger(__name__)


def main(args=None):

    import argparse

    FORMAT = "%(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler(console=Console(width=89))],
    )

    parser = argparse.ArgumentParser(
        description=(
            "Generate image prompts from a theme using a local LLM via Ollama, "
            "one batch per display model registered on the canvas coordinator, "
            "and post them back to the coordinator."
        )
    )
    parser.add_argument(
        "--theme", type=str, required=True, help="Theme or style string to generate prompts for"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of prompts to generate per display model (default: 5)",
    )
    parser.add_argument(
        "--canvas-server-url",
        type=str,
        required=True,
        help="Canvas coordinator URL (fetch frames, post prompts)",
    )
    parser.add_argument(
        "--system-prompt",
        type=Path,
        required=True,
        help="System prompt file (e.g. assets/prompt_system.txt)",
    )
    parser.add_argument(
        "--task-prompt",
        type=Path,
        required=True,
        help="Task prompt template file (e.g. assets/prompt_task.txt)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Ollama model to use (default: {DEFAULT_MODEL})",
    )

    args = parser.parse_args(args)

    assert args.system_prompt.is_file(), f"System prompt file not found: {args.system_prompt}"
    assert args.task_prompt.is_file(), f"Task prompt file not found: {args.task_prompt}"

    system_prompt = args.system_prompt.read_text()
    task_template = args.task_prompt.read_text()

    display_models = get_display_models(args.canvas_server_url)

    assert display_models, "No display models registered on the canvas coordinator"

    logger.info(f"Found {len(display_models)} display model(s) registered:")
    for display_model in display_models:
        logger.info(f"  {display_model.value} -> {color_range_from_display(display_model)}")

    logger.info(f"Theme: {args.theme}")
    logger.info(f"Generating {args.count} prompts per display model using {args.model}")

    with ollama_session(args.model):
        for display_model in display_models:
            color_range = color_range_from_display(display_model)

            logger.info(f"Generating for {display_model.value} ({color_range})...")

            prompts = generate_prompts_for_themes(
                [args.theme],
                args.count,
                color_range=color_range,
                system_prompt=system_prompt,
                task_template=task_template,
                model=args.model,
            )

            post_prompts(
                prompts,
                display_model=display_model,
                server_url=args.canvas_server_url,
            )

    logger.info("Done")


if __name__ == "__main__":
    main()
