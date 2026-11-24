import logging
from contextlib import asynccontextmanager

from canvasserver.config import get_settings
from canvasserver.constants import APP_NAME
from canvasserver.cron_jobs import create_scheduler
from canvasserver.routes import api_router
from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware

from .models.db import session_scope
from .version import __version__

logger = logging.getLogger("uvicorn.info")


@asynccontextmanager
async def lifespan(app: FastAPI):

    # startup
    logger.info("Initialize settings")
    _ = get_settings()

    logger.info("Starting background jobs")
    with session_scope() as session:
        scheduler = create_scheduler(session)
    scheduler.start()
    app.state.scheduler = scheduler

    yield

    # shutdown
    logger.info("Killing background jobs")
    scheduler.shutdown()
    app.state.scheduler = None


app = FastAPI(
    title=APP_NAME, version=__version__, lifespan=lifespan, dependencies=[Depends(get_settings)]
)


# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_main():
    logging.info("Logging from the root logger")
    return {"msg": "Hello World"}


app.include_router(api_router, prefix="")
