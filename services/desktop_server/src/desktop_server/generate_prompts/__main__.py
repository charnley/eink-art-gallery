import logging
from pathlib import Path

from desktop_server import cli_utils
from desktop_server.canvas_client import color_range_from_display, post_prompts
from desktop_server.generate_prompts import (
    DEFAULT_MODEL,
    generate_prompts_for_themes,
    ollama_session,
)
from shared_constants import WaveshareDisplay

logger = logging.getLogger(__name__)


def main(args=None):

    import argparse

    cli_utils.setup_logging()

    parser = argparse.ArgumentParser(
        description="Generate image prompts from a theme using a local LLM via Ollama."
    )
    parser.add_argument(
        "--theme", type=str, required=True, help="Theme or style string to generate prompts for"
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
        "--count", type=int, default=5, help="Number of prompts to generate (default: 5)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Ollama model to use (default: {DEFAULT_MODEL})",
    )

    # Output options — at least one required
    parser.add_argument(
        "--canvas-server-url", type=str, help="Canvas coordinator URL to POST prompts to"
    )
    parser.add_argument(
        "--image-model",
        type=str,
        help="Image model name (required with --canvas-server-url)",
        default="SD3",
    )
    parser.add_argument(
        "--display-model",
        type=WaveshareDisplay,
        choices=list(WaveshareDisplay),
        help="Display model (required with --canvas-server-url)",
    )
    parser.add_argument(
        "--output-filename", type=Path, help="Optional local output .txt file for debugging"
    )

    args = parser.parse_args(args)

    assert (
        args.canvas_server_url or args.output_filename
    ), "At least one of --canvas-server-url or --output-filename must be provided"

    if args.canvas_server_url:
        assert args.display_model, "--display-model is required when using --canvas-server-url"
        assert args.image_model, "--image-model is required when using --canvas-server-url"

    system_prompt = args.system_prompt.read_text()
    task_template = args.task_prompt.read_text()

    color_range = color_range_from_display(args.display_model) if args.display_model else "BW"

    logger.info(f"Theme: {args.theme}")
    logger.info(f"Display model: {args.display_model} -> color range: {color_range}")
    logger.info(f"Generating '{args.count}' prompts using '{args.model}'")

    with ollama_session(args.model):
        prompts = generate_prompts_for_themes(
            [args.theme],
            args.count,
            color_range=color_range,
            system_prompt=system_prompt,
            task_template=task_template,
            model=args.model,
        )

    logger.info(f"Generated {len(prompts)} prompts total")

    if args.output_filename:
        args.output_filename.parent.mkdir(parents=True, exist_ok=True)
        args.output_filename.write_text("\n".join(prompts) + "\n")
        logger.info(f"Written to {args.output_filename}")

    if args.canvas_server_url:
        post_prompts(
            prompts,
            image_model=args.image_model,
            display_model=args.display_model,
            server_url=args.canvas_server_url,
        )


if __name__ == "__main__":
    main()
