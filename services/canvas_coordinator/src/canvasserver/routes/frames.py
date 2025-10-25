import uuid
from typing import Annotated

from canvasserver.jobs.apis import get_status
from fastapi import APIRouter, Body, Depends, HTTPException, status
from shared_constants import WaveshareDisplay
from sqlalchemy.orm import Session
from sqlmodel import select

from ..models.db import get_session
from ..models.db_models import Frame, FrameType
from ..models.schemas import Frames

prefix = "/frame"
router = APIRouter(prefix=prefix, tags=["frames"])


@router.get("/", response_model=Frames)
def read_items(limit=100, session: Session = Depends(get_session)):
    devices = session.query(Frame).limit(limit).all()
    session.close()
    return Frames(devices=devices, count=len(devices))


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
