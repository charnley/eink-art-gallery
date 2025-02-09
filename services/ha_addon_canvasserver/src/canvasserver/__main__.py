import argparse
import logging
import sys

import uvicorn
from rich.logging import RichHandler

from .models.db import create_db_and_tables
from .version import __version__

logger = logging.getLogger(__name__)


def main(args=None):

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--init-db", action="store_true")
    parser.add_argument("--db-filename", action="store_true")
    args = parser.parse_args(args)

    FORMAT = "%(message)s"
    logging.basicConfig(level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])

    if args.init_db:
        logger.info("Generating table...")
        create_db_and_tables(None)
        logger.info("Done")
        sys.exit(0)

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
