import argparse
import logging
import threading

import requests
from rich.logging import RichHandler

logger = logging.getLogger(__name__)

ENDPOINT_CHECK = "/actions/queue_check"


def request_task(url, json, headers):
    requests.post(url, json=json, headers=headers)


def fire_and_forget(url, json, headers):
    threading.Thread(target=request_task, args=(url, json, headers)).start()


def main(args=None):

    # TODO Parameterize the database path (Needed for the docker anyway)

    parser = argparse.ArgumentParser()
    # parser.add_argument("-v", "--version", action="version", version=__version__)
    # parser.add_argument("--reload", action="store_true")
    # parser.add_argument("--start", action="store_true")
    parser.add_argument("--canvas-server-url", default="http://localhost:8000", type=str)
    parser.add_argument("--canvas-server-fill-count", type=int, default=5)
    # parser.add_argument("--init-db", action="store_true")
    # parser.add_argument("--prompts-filename", type=Path)
    args = parser.parse_args(args)

    FORMAT = "%(message)s"
    logging.basicConfig(level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])

    logger.info(f"Fetching from {args.canvas_server_url + ENDPOINT_CHECK}")
    response = requests.get(args.canvas_server_url + ENDPOINT_CHECK)

    assert response.status_code == 200, response.json()

    data = response.json()
    # prompts = data["prompts"]

    # Nothing to do

    if data["count"] == 0:
        return

    # Load model


if __name__ == "__main__":
    main()
