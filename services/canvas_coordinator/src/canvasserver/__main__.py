import argparse
import logging
from pathlib import Path

import uvicorn
from canvasserver.config import get_settings
from canvasserver.models.content import Prompt
from rich.console import Console
from rich.logging import RichHandler

from .models.db import create_db_and_tables, get_engine, get_session, has_tables
from .version import __version__

logger = logging.getLogger(__name__)


def main(args=None):

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=__version__)

    parser.add_argument("--init-db", action="store_true")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--prompts-filename", type=Path)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args(args)

    FORMAT = "%(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=FORMAT,
        datefmt="[%Y-%m-%d %H:%I]",
        handlers=[RichHandler(console=Console(width=120))],
    )

    # If database is not defined
    settings = get_settings()
    database_path = settings.database_path

    if not database_path.is_file():
        logger.info("Database file does not exist, generating table...")
        create_db_and_tables(None)

    # Check database has schema
    engine = get_engine()
    if not has_tables(engine):
        logger.info("There is a file, but no tables found, generating tables...")
        create_db_and_tables(None)

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
            port=args.port,
            reload=args.reload,
            log_level=None,
            log_config=log_config,
            workers=args.workers,
        )


if __name__ == "__main__":
    main()
