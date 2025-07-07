import uuid

from canvasserver.jobs.apis import get_status
from fastapi import APIRouter, Depends, HTTPException, status
from shared_constants import WaveshareDisplay
from sqlalchemy.orm import Session
from sqlmodel import select

from ..models.content import PushFrame, PushFrames
from ..models.db import get_session

prefix = "/pushDevices"
router = APIRouter(prefix=prefix, tags=["devices"])


@router.get("/", response_model=PushFrames)
def read_items(limit=100, session: Session = Depends(get_session)):
    devices = session.query(PushFrame).limit(limit).all()
    session.close()
    return PushFrames(devices=devices, count=len(devices))


@router.get("/{id}", response_model=PushFrame)
def read_item(id: uuid.UUID, session: Session = Depends(get_session)):
    item = session.get(PushFrame, id)
    session.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{id}", response_model=PushFrame)
def delete_item(id: uuid.UUID, session: Session = Depends(get_session)):
    item = session.get(PushFrame, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    session.delete(item)
    session.commit()
    session.close()

    return item


@router.post("/")
def create_item(
    item: PushFrame, session: Session = Depends(get_session), ignore_status: bool = False
):

    hostname = item.hostname

    # Check if it already exists
    item_check = session.execute(select(PushFrame).filter_by(hostname=hostname)).all()
    if len(item_check):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item already exists.")

    # Check that it is alive
    api_status = get_status(hostname)
    if not api_status and not ignore_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hostname does not return a good status",
        )

    assert api_status is not None

    # Check if we can read the type
    if "display_type" in api_status:
        display_model = api_status["display_type"]
        display_model = WaveshareDisplay(display_model)
        item.model = display_model

    # Ensure it is correct type before commit
    display_model = WaveshareDisplay(item.model)
    if not isinstance(display_model, WaveshareDisplay):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not supported display model",
        )

    session.add(item)

    try:

        session.commit()
        session.refresh(item)

    except ValueError:

        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving the item.",
        )

    session.close()
    return item
