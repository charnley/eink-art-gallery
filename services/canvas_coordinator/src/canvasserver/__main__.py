import argparse
import logging
from pathlib import Path

import uvicorn
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from canvasserver.config import get_settings
from canvasserver.models.content import Prompt

from .models.db import create_db_and_tables, get_engine, get_session, has_tables
from .version import __version__

# from canvasserver.jobs import refresh_active_prompt, send_images_to_push_devices

logger = logging.getLogger(__name__)


def job1():
    logger.info("Job 1")

    return


def job2():
    logger.info("Job 1")

    return


def main(args=None):

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=__version__)

    parser.add_argument("--init-db", action="store_true")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--prompts-filename", type=Path)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--logging-config", type=Path, default=Path("logging_config.yaml"))
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

        logger.info(f"Version {__version__}")

        # Load background jobs
        scheduler = BackgroundScheduler()

        cron = "*/10 * * * *"
        cron = "*/1 * * * *"

        scheduler.add_job(job1, CronTrigger.from_crontab(cron))
        scheduler.add_job(job2, CronTrigger.from_crontab("0 4 * * *"))

        logger.info("Starting background jobs")
        scheduler.start()

        # Run Uvicorn server
        uvicorn.run(
            "canvasserver.main:app",
            host="0.0.0.0",
            port=args.port,
            reload=args.reload,
            log_level=None,
            log_config=str(Path("./logging_config.yaml")),
            workers=args.workers,
        )
        scheduler.shutdown()


if __name__ == "__main__":
    main()
