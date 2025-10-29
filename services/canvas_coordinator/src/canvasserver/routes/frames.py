import logging
import uuid
from typing import Annotated

from canvasserver.constants import DEFAULT_PULLFRAME_CRON
from canvasserver.jobs.apis import get_status
from canvasserver.models.queries import fetch_image_for_frame, get_frame_by_mac_address
from canvasserver.time_funcs import get_seconds_until_next
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.responses import Response
from shared_constants import IMAGE_CONTENT_TYPE, IMAGE_HEADER, WaveshareDisplay
from shared_image_utils import prepare_image
from shared_image_utils.format import image_to_bytes
from shared_matplotlib_utils import get_basic_text
from sqlalchemy.orm import Session
from sqlmodel import select

from ..models.db import get_session
from ..models.db_models import Frame, FrameType
from ..models.schemas import Frames, FrameUpdate

logger = logging.getLogger(__name__)

prefix = "/frame"
router = APIRouter(prefix=prefix, tags=["frames"])


def get_display_model(request) -> WaveshareDisplay | None:
    """
    Read the ESPHome configured user-agent definition:

        Frame/${display_model}

    For example:

        Frame/WaveShare13BlackWhite960x680

    """

    user_agent = request.headers.get("user-agent")
    display_type = user_agent.split("/")[-1]

    if display_type not in WaveshareDisplay:
        logger.error("Unable to find the display type from User-Agent")
        logger.error(f"User-agent: {user_agent}")
        return None

    return WaveshareDisplay(display_type)


# TODO Insert query parameters, for sub-types


@router.get("/", response_model=Frames)
def read_items(session: Session = Depends(get_session)):
    frames = session.query(Frame).all()
    session.close()
    return Frames(frames=frames, count=len(frames))


@router.get("/{id}", response_model=Frame)
def read_item(id: uuid.UUID, session: Session = Depends(get_session)):
    item = session.get(Frame, id)
    session.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{id}", response_model=Frame)
def delete_item(id: uuid.UUID, session: Session = Depends(get_session)):
    item = session.get(Frame, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    session.delete(item)
    session.commit()
    session.close()

    return item


@router.patch("/{id}", response_model=Frame)
def update_frame(
    id: uuid.UUID,
    frame_update: FrameUpdate,
    session: Session = Depends(get_session),
):
    frame = session.get(Frame, id)

    if frame is None:
        raise HTTPException(status_code=404, detail="Frame not found")

    data = frame_update.model_dump(exclude_unset=True)
    frame.sqlmodel_update(data)

    session.add(frame)
    session.commit()
    session.refresh(frame)
    session.close()
    return frame


def _validate_push_frame(frame):

    # Check that it is alive
    endpoint_status = get_status(frame.endpoint)

    if endpoint_status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hostname does not return a good status",
        )

    # Check if we can read the type
    if "display_type" in endpoint_status:
        display_model = endpoint_status["display_type"]
        display_model = WaveshareDisplay(display_model)
        frame.model = display_model

    return


annotated_frame_examples = [
    {"endpoint": "192.168.1.102:8080"},
    {"mac": "hello", "model": str(WaveshareDisplay.WaveShare13BlackWhite960x680)},
]

AnnotatedFrame = Annotated[
    Frame,
    Body(
        examples=annotated_frame_examples,
    ),
]


@router.post("/")
def create_item(frame: AnnotatedFrame, session: Session = Depends(get_session)):

    endpoint = frame.endpoint  # PushFrame
    mac = frame.mac  # PullFrame

    if frame.type is None and frame.endpoint is not None:
        frame.type = FrameType.PUSH

    if frame.type is None and frame.mac is not None:
        frame.type = FrameType.PULL

    if endpoint is None and mac is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either MAC or endpoint needs to be defined",
        )

    # Check if it already exists
    if endpoint is not None and len(
        session.execute(select(Frame).filter_by(endpoint=endpoint)).all()
    ):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item already exists.")

    if mac is not None and len(session.execute(select(Frame).filter_by(mac=mac)).all()):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item already exists.")

    if frame.type == FrameType.PUSH:
        # Validate endpoint, and assume DisplayType
        _validate_push_frame(frame)

    # Ensure it is correct type before commit
    display_model = WaveshareDisplay(frame.model)
    if not isinstance(display_model, WaveshareDisplay):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not supported display model",
        )

    session.add(frame)

    try:

        session.commit()
        session.refresh(frame)

    except ValueError:

        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving the item.",
        )

    session.close()
    return frame


@router.get("/mac/{mac_address}/get-sleep-duration", response_model=int)
def get_sleep(mac_address: str, request: Request, session: Session = Depends(get_session)):

    display_model = get_display_model(request)
    frame = get_frame_by_mac_address(session, mac_address, display_model)

    if frame is None:
        logger.warning("Frame definition is wrong, returning default CRON")
        return get_seconds_until_next(DEFAULT_PULLFRAME_CRON)

    logging.info(f"Found Frame: {frame} - {display_model} - {frame.group}")

    if frame.group is None:
        logger.warning("Frame is not registered a group, returning default CRON")
        return get_seconds_until_next(DEFAULT_PULLFRAME_CRON)

    seconds = get_seconds_until_next(frame.group.schedule_frame)

    session.commit()
    session.close()

    return seconds


@router.get(
    "/mac/{mac_address}/display.png",
    responses={
        200: {"content": {IMAGE_CONTENT_TYPE: {}}},
        404: {"content": {IMAGE_CONTENT_TYPE: {}}},
    },
    response_class=Response,
)
def get_image(mac_address: str, request: Request, session: Session = Depends(get_session)):

    # Note: ESPHome will react to 400, so always return 200

    display_model = get_display_model(request)
    frame: Frame | None = get_frame_by_mac_address(session, mac_address, display_model)

    print(frame)

    if frame is None:
        logger.error("Unable to figure out what kind of frame this is, returning default")
        image = get_basic_text(f"Testing: {mac_address}")

    else:
        image = fetch_image_for_frame(session, frame)

    assert Frame is not None

    image = prepare_image(image, frame.model)
    image_bytes = image_to_bytes(image)

    # TODO Fall back if frame is undefined, but display_model is

    session.commit()
    session.close()

    return Response(image_bytes, headers=IMAGE_HEADER, media_type=IMAGE_CONTENT_TYPE)
