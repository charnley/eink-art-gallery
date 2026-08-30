import logging
import warnings

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(width: int = 89) -> None:
    """Configure root logging with a RichHandler."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=Console(width=width))],
    )


def ignore_user_warnings() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
