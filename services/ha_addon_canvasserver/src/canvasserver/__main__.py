import argparse
import logging
import sys

import uvicorn

from .models.db import create_db_and_tables
from .version import __version__

logger = logging.getLogger(__name__)


def main(args=None):

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--init-db", action="store_true")
    args = parser.parse_args(args)

    logging.basicConfig(level=logging.DEBUG)

    if args.init_db:
        logger.info("Generating table")
        create_db_and_tables()
        sys.exit(0)

    logger.info(f"Starting {__name__}")
    logger.info(f"Version {__version__}")

    # Run Uvicorn server
    uvicorn.run(
        "canvasserver.main:app",
        host="0.0.0.0",
        port=8000,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
