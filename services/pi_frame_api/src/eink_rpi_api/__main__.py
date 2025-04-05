import argparse
import logging
from pathlib import Path

import uvicorn
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

from . import jobs

def main(args=None):

    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--version", action="version", version=__version__)

    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--logging-config", type=Path, default=Path("./logging_config.yaml"))

    args = parser.parse_args(args)

    # Enable logging
    if args.logging_config:
        with open(args.logging_config, "rt") as f:
            config = yaml.safe_load(f.read())

        logging.config.dictConfig(config)

    scheduler = BackgroundScheduler()

    reset_cron = "5 2 * * *"
    if reset_cron:
        scheduler.add_job(
            lambda: jobs.clear(),
            CronTrigger.from_crontab(reset_cron),
        )

    logger.info("Starting background jobs")
    scheduler.start()

    uvicorn.run(
        "picture_api:app",
        host="0.0.0.0",
        port=args.port,
        reload=args.reload,
        log_level=None,
        log_config=str(args.logging_config),
        workers=args.workers,
    )

    logger.info("Killing background jobs")
    scheduler.shutdown()


if __name__ == "__main__":
    main()
