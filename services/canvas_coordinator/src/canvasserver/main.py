import logging

from canvasserver.config import get_settings
from canvasserver.constants import APP_NAME
from canvasserver.routes import api_router
from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware

from .version import __version__

# logger = logging.getLogger(__name__)
logger = logging.getLogger("uvicorn.info")


# @asynccontextmanager
async def lifespan(app: FastAPI):

    # startup
    logger.info("Initialize settings")
    settings = get_settings()

    # Read the cron jobs
    # - rotate active prompt
    # - send to push devices

    yield

    # shutdown
    return


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
