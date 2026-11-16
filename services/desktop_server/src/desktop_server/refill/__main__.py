import argparse
from datetime import timedelta
from pathlib import Path

from desktop_server import cli_utils
from desktop_server.generate_prompts import DEFAULT_MODEL
from desktop_server.refill.images import refill_images
from desktop_server.refill.prompts import refill_prompts
from desktop_server.refill.time_utils import parse_time_period


def _add_prompts_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--theme", type=str, required=True, help="Theme or style string to generate prompts for"
    )
    count_time_group = parser.add_mutually_exclusive_group()
    count_time_group.add_argument(
        "--count",
        type=int,
        default=None,
        help="Number of prompts to generate per display model (default: 5, unless --time is given)",
    )
    count_time_group.add_argument(
        "--time",
        type=str,
        default=None,
        help="Time period to cover, e.g. '1 week', '3 days', '2 hours'",
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Refill the canvas coordinator: generate prompts from a theme via Ollama, "
            "generate images for prompts missing them."
        )
    )
    parser.add_argument(
        "--server-url",
        type=str,
        required=True,
        help="Canvas coordinator URL (fetch frames/prompts, post prompts/images)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    prompts_parser = subparsers.add_parser(
        "prompts", help="Generate prompts from a theme and post them"
    )
    _add_prompts_arguments(prompts_parser)

    subparsers.add_parser("images", help="Generate images for prompts missing them")

    all_parser = subparsers.add_parser(
        "all", help="Refill prompts first, then generate missing images"
    )
    _add_prompts_arguments(all_parser)

    return parser


def main(args=None):
    cli_utils.setup_logging()
    cli_utils.ignore_user_warnings()

    parser = build_parser()
    args = parser.parse_args(args)

    if args.command in ("prompts", "all"):
        assert args.system_prompt.is_file(), f"System prompt file not found: {args.system_prompt}"
        assert args.task_prompt.is_file(), f"Task prompt file not found: {args.task_prompt}"

        count: int | None = args.count
        time_period: timedelta | None = None

        if args.time:
            time_period = parse_time_period(args.time)
        elif count is None:
            count = 5

        refill_prompts(
            theme=args.theme,
            count=count,
            canvas_server_url=args.server_url,
            system_prompt=args.system_prompt.read_text(),
            task_template=args.task_prompt.read_text(),
            model=args.model,
            time_period=time_period,
        )

    if args.command in ("images", "all"):
        refill_images(args.server_url)


if __name__ == "__main__":
    main()
