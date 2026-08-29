import logging
from pathlib import Path

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
        description="Generate image prompts from a theme file using a local LLM via Ollama."
    )
    parser.add_argument(
        "--theme", type=str, required=True, help="Theme or style string to generate prompts for"
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="Output .txt file for generated prompts"
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
        help="Task prompt template file (e.g. assets/prompt_task.txt), with {n}, {theme}, {color_range} placeholders",
    )
    parser.add_argument(
        "--color-range",
        type=str,
        required=True,
        choices=["BW", "BWR", "COLOR"],
        help="Color range: BW, BWR, or COLOR",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of prompts to generate per theme line (default: 5)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Ollama model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--append", action="store_true", help="Append to output file instead of overwriting"
    )

    args = parser.parse_args(args)

    assert args.system_prompt.is_file(), f"System prompt file not found: {args.system_prompt}"
    assert args.task_prompt.is_file(), f"Task prompt file not found: {args.task_prompt}"

    themes = [args.theme]
    system_prompt = args.system_prompt.read_text()
    task_template = args.task_prompt.read_text()

    logger.info(f"Theme: {args.theme}")
    logger.info(f"Color range: {args.color_range}")
    logger.info(f"Generating {args.count} prompts per theme using {args.model}")

    with ollama_session(args.model):
        prompts = generate_prompts_for_themes(
            themes,
            args.count,
            color_range=args.color_range,
            system_prompt=system_prompt,
            task_template=task_template,
            model=args.model,
        )

    logger.info(f"Generated {len(prompts)} prompts total")

    mode = "a" if args.append else "w"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, mode) as f:
        f.write("\n".join(prompts) + "\n")

    logger.info(f"{'Appended' if args.append else 'Written'} to {args.output}")


if __name__ == "__main__":
    main()
