import argparse
import logging
from logging import config as logging_config
from pathlib import Path

import yaml
from canvasserver.config import get_settings
from canvasserver.models.db_models import Image, Prompt
from shared_matplotlib_utils import get_basic_text
from sqlalchemy import select

from ..models.db import create_db_and_tables, get_engine, get_session, has_tables

logger = logging.getLogger(__name__)


def main(args=None):

    parser = argparse.ArgumentParser()

    parser.add_argument("--logging-config", type=Path, default=Path("logging_config.yaml"))

    parser.add_argument("--fake-it", action="store_true")
    parser.add_argument("--no-fake-photos", type=int, default=6)

    parser.add_argument("--init-db", action="store_true")
    parser.add_argument("--prompts-filename", type=Path)

    args = parser.parse_args(args)

    # Enable logging
    if args.logging_config:
        with open(args.logging_config, "rt") as f:
            config = yaml.safe_load(f.read())

        logging_config.dictConfig(config)

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

    if args.fake_it:

        with get_session() as session:

            # All prompts:
            all_prompts = session.execute(select(Prompt)).all()

            for (prompt,) in all_prompts:
                logging.info(prompt)

                # Create fake image
                for i in range(args.no_fake_photos):

                    length = 4
                    string = str(prompt.id)
                    text = " ".join(string[i : i + length] for i in range(0, len(string), length))

                    pillowImage = get_basic_text(f"{text} \n {i}")
                    image = Image(prompt=prompt.id)
                    image.image = pillowImage
                    session.add(image)

            session.commit()


if __name__ == "__main__":
    main()
