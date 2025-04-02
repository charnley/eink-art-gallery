import argparse
import logging
from pathlib import Path

import uvicorn
import yaml

logger = logging.getLogger(__name__)


def main(args=None):

    parser = argparse.ArgumentParser()

    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--logging-config", type=Path, default=Path("./logging_config.yaml"))

    args = parser.parse_args(args)

    # Enable logging
    if args.logging_config:
        with open(args.logging_config, "rt") as f:
            config = yaml.safe_load(f.read())

        logging.config.dictConfig(config)

    uvicorn.run(
        "desktop_server.api:app",
        host="0.0.0.0",
        port=args.port,
        reload=args.reload,
        log_level=None,
        log_config=str(args.logging_config),
        workers=args.workers,
    )


if __name__ == "__main__":
    main()
