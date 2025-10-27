import datetime
import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

prefix = "/system"

router = APIRouter(prefix=prefix, tags=["system"])


@router.get("/get-time", response_model=int, tags=["system"])
def _get_time():
    now = datetime.datetime.now()
    return int(now.timestamp())
