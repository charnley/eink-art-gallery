import argparse
from pathlib import Path

from desktop_server import cli_utils
from desktop_server.generate_prompts import DEFAULT_MODEL
from desktop_server.refill.images import refill_images
from desktop_server.refill.prompts import refill_prompts


def _add_prompts_arguments(parser: argparse.ArgumentParser) -> None:
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

        refill_prompts(
            theme=args.theme,
            count=args.count,
            canvas_server_url=args.server_url,
            system_prompt=args.system_prompt.read_text(),
            task_template=args.task_prompt.read_text(),
            model=args.model,
        )

    if args.command in ("images", "all"):
        refill_images(args.server_url)


if __name__ == "__main__":
    main()
