import uuid

from fastapi import APIRouter, Depends, HTTPException, status
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
def create_item(item: PushFrame, session: Session = Depends(get_session)):

    hostname = item.hostname

    item_check = session.execute(select(PushFrame).filter_by(hostname=hostname)).all()

    if len(item_check):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item already exists.")

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
