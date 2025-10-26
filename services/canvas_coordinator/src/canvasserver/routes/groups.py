import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..jobs.push_device_logic import send_images_to_push_frames
from ..models.db import get_session
from ..models.db_models import Frame, FrameGroup, FrameType
from ..models.schemas import FrameAssign, FrameGroups, FrameHttpCode, Frames

logger = logging.getLogger(__name__)

prefix = "/group"
router = APIRouter(prefix=prefix, tags=["groups"])


@router.get("/", response_model=FrameGroups)
def read_items(limit=100, session: Session = Depends(get_session)):
    groups = session.query(FrameGroup).limit(limit).all()
    session.close()
    return FrameGroups(groups=groups, count=len(groups))


@router.get("/{id}", response_model=FrameGroup)
def read_item(id: uuid.UUID, session: Session = Depends(get_session)):
    item = session.get(FrameGroup, id)
    session.close()
    if not item:
        raise HTTPException(status_code=404, detail="Group not found")
    return item


@router.delete("/{id}", response_model=FrameGroup)
def delete_item(id: uuid.UUID, session: Session = Depends(get_session)):

    group = session.get(FrameGroup, id)

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    for frame in group.frames:
        frame.group_id = None

    session.delete(group)

    session.commit()
    session.close()

    return group


annotated_group_examples = [
    {"name": "LivingRoomFrames", "cron_schedule": "30 4 * * *", "default": True},
]

AnnotatedFrameGroup = Annotated[
    FrameGroup,
    Body(
        examples=annotated_group_examples,
    ),
]


@router.post("/")
def create_item(group: AnnotatedFrameGroup, session: Session = Depends(get_session)):

    session.add(group)

    try:

        session.commit()
        session.refresh(group)

    except ValueError:

        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving the item.",
        )

    session.close()
    return group


# Manage group


@router.get("/{id}/frames", response_model=Frames)
def read_frames(id: uuid.UUID, session: Session = Depends(get_session)):
    group = session.get(FrameGroup, id)

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    frames = Frames(frames=group.frames, count=len(group.frames))
    session.close()

    return frames


@router.post("/{id}/frames", response_model=Frame)
def add_frame(id: uuid.UUID, frame_assign: FrameAssign, session: Session = Depends(get_session)):

    group = session.get(FrameGroup, id)
    frame = session.get(Frame, frame_assign.id)

    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    if frame is None:
        raise HTTPException(status_code=404, detail="Frame not found")

    frame.group_id = group.id

    session.commit()
    session.close()

    return frame


@router.delete("/{id}/frame/{frame_id}", response_model=Frame)
def delete_frame(id: uuid.UUID, frame_id: uuid.UUID, session: Session = Depends(get_session)):

    frame = session.get(Frame, frame_id)

    if not frame:
        raise HTTPException(status_code=404, detail="Frame not found")

    frame.group_id = None

    session.commit()
    session.close()

    return frame


# Actions


@router.get("/{id}/refresh", response_model=list[FrameHttpCode])
def refresh_item(id: uuid.UUID, session: Session = Depends(get_session)):

    group = session.get(FrameGroup, id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Get PULL frames
    frames = group.frames
    frames = [frame for frame in frames if frame.type == FrameType.PUSH]

    if not len(frames):
        return []

    frame_returns = send_images_to_push_frames(frames, session)
    session.close()

    return frame_returns
