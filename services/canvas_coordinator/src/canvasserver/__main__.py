import argparse
import logging
from pathlib import Path

import uvicorn
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from canvasserver.config import get_settings
from canvasserver.jobs import refresh_active_prompt, send_images_to_push_devices

from .models.db import create_db_and_tables, get_engine, get_session, has_tables
from .version import __version__

logger = logging.getLogger(__name__)


def outside_session_call(func):
    session = get_session()
    func(session)
    session.commit()
    session.close()


def main(args=None):

    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--version", action="version", version=__version__)

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

    if args.start:

        logger.info(f"Version {__version__}")

        scheduler = BackgroundScheduler()

        if settings.cron_update_push:
            scheduler.add_job(
                lambda: outside_session_call(send_images_to_push_devices),
                CronTrigger.from_crontab(settings.cron_update_push),
            )

        if settings.cron_update_prompt:
            scheduler.add_job(
                lambda: outside_session_call(refresh_active_prompt),
                CronTrigger.from_crontab(settings.cron_update_prompt),
            )

        logger.info("Starting background jobs")
        scheduler.start()

        uvicorn.run(
            "canvasserver.main:app",
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
