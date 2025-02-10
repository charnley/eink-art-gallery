import argparse
import logging
from pathlib import Path

import uvicorn
from canvasserver.models.content import Prompt
from rich.console import Console
from rich.logging import RichHandler

from .models.db import create_db_and_tables, get_session
from .version import __version__

logger = logging.getLogger(__name__)


def main(args=None):

    # TODO Parameterize the database path (Needed for the docker anyway)

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--init-db", action="store_true")
    parser.add_argument("--prompts-filename", type=Path)
    args = parser.parse_args(args)

    FORMAT = "%(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler(console=Console(width=120))],
    )

    if args.init_db:
        logger.info("Generating table...")
        create_db_and_tables(None)
        logger.info("Generated")

    # Read prompt file and put into database
    if args.prompts_filename is not None:

        logger.info("Reading pre-defined prompts...")

        with get_session() as session, open(args.prompts_filename, "r") as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]

            for line in lines:
                prompt = Prompt(prompt=line, model="SD3")
                session.add(prompt)

            session.commit()

            logger.info(f"Database enriched with {len(lines)} prompts")

    if args.start:
        log_config = dict(uvicorn.config.LOGGING_CONFIG)
        log_config["loggers"]["uvicorn"] = {"handlers": []}
        log_config["loggers"]["uvicorn.error"] = {"handlers": []}
        log_config["loggers"]["uvicorn.access"] = {"handlers": []}

        logger.info(f"Starting {__name__}")
        logger.info(f"Version {__version__}")

        # Run Uvicorn server
        uvicorn.run(
            "canvasserver.main:app",
            host="0.0.0.0",
            port=8000,
            reload=args.reload,
            log_level=None,
            log_config=log_config,
        )


if __name__ == "__main__":
    main()
