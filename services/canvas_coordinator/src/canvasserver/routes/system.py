import datetime
import logging

from canvasserver.time_funcs import get_seconds_until_next
from fastapi import APIRouter

logger = logging.getLogger(__name__)

prefix = "/system"

router = APIRouter(prefix=prefix, tags=["system"])


@router.get("/get-time", response_model=int, tags=["system"])
def _get_time():
    now = datetime.datetime.now()
    return int(now.timestamp())


@router.get("/get-sleep-seconds", response_model=int, tags=["system"])
def _get_sleep():

    # TODO Now I can do it per-frame. CRON per-frame/per-group
    # TODO Now calculate buffer
    # TODO Check interval cron, there needs to be a start point?

    # Cron's need a starte date, because */30 interval will make the pullframes desync fast

    cron_string = "30 4 * * *"
    seconds = get_seconds_until_next(cron_string)

    return seconds
