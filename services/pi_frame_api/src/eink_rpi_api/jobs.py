import logging
from . import displaying
logger = logging.getLogger(__name__)

def clear():
    logger.info("Nightly reset")
    displaying.init()
    displaying.clear()
    displaying.sleep()
