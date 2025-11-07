import logging
import uuid
from typing import Annotated

from apscheduler.triggers.cron import CronTrigger
from canvasserver.models.queries import get_group_prompts, rotate_prompt_for_group
from canvasserver.time_funcs import get_schedule_datetimes
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..jobs.push_device_logic import send_images_to_push_frames
from ..models.db import get_session
from ..models.db_models import Frame, FrameGroup, FrameType, Prompt
from ..models.schemas import (
    FrameAssign,
    FrameGroups,
    FrameGroupSchedule,
    FrameGroupUpdate,
    FrameHttpCode,
    Frames,
    PromptId,
)

logger = logging.getLogger(__name__)

prefix = "/groups"
router = APIRouter(prefix=prefix, tags=["groups"])


def validate_cron(cron: str) -> None:
    """Return error trying to create a cron"""

    # Raises: HTTPException

    # try except CronTrigger.from_crontab(cron_string)
    # ValueError: Unrecognized expression "*30" for field "minute

    try:
        _ = CronTrigger.from_crontab(cron)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return None


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

    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    for frame in group.frames:
        frame.group_id = None

    session.delete(group)

    session.commit()
    session.close()

    return group


annotated_group_examples = [
    {
        "name": "LivingRoomFrames",
        "schedule_frame": "30 4 * * *",
        "schedule_prompt": "30 0 * * *",
        "default": True,
    },
]

AnnotatedFrameGroup = Annotated[
    FrameGroupUpdate,
    Body(
        examples=annotated_group_examples,
    ),
]


@router.post("/")
def create_item(new_group: FrameGroup, session: Session = Depends(get_session)):

    validate_cron(new_group.schedule_frame)
    validate_cron(new_group.schedule_prompt)

    session.add(new_group)

    try:

        session.commit()
        session.refresh(new_group)

    except ValueError:

        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving the item.",
        )

    session.close()
    return new_group


@router.patch("/{id}", response_model=FrameGroup)
def update_group(
    id: uuid.UUID,
    group_update: AnnotatedFrameGroup,
    session: Session = Depends(get_session),
):
    group = session.get(FrameGroup, id)

    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    # Validate
    if group_update.schedule_frame:
        validate_cron(group_update.schedule_frame)

    if group_update.schedule_prompt:
        validate_cron(group_update.schedule_prompt)

    data = group_update.model_dump(exclude_unset=True)

    group.sqlmodel_update(data)

    session.add(group)
    session.commit()
    session.refresh(group)
    session.close()
    return group


@router.get("/{id}/schedule", response_model=FrameGroupSchedule)
def get_schedule(id: uuid.UUID, count: int = 10, session: Session = Depends(get_session)):
    group = session.get(FrameGroup, id)

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    schedule = FrameGroupSchedule()

    if group.schedule_frame:
        _schedule = get_schedule_datetimes(group.schedule_frame, count=count)
        schedule.schedule_frame = [int(x.timestamp()) for x in _schedule]

    if group.schedule_prompt:
        _schedule = get_schedule_datetimes(group.schedule_prompt, count=count)
        schedule.schedule_prompt = [int(x.timestamp()) for x in _schedule]

    session.close()

    return schedule


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


@router.delete("/{id}/frames/{frame_id}", response_model=Frame)
def delete_frame(id: uuid.UUID, frame_id: uuid.UUID, session: Session = Depends(get_session)):

    frame = session.get(Frame, frame_id)

    if not frame:
        raise HTTPException(status_code=404, detail="Frame not found")

    frame.group_id = None

    session.commit()
    session.close()

    return frame


@router.post("/{id}/refresh", response_model=list[FrameHttpCode])
def refresh_item(id: uuid.UUID, session: Session = Depends(get_session)):

    group = session.get(FrameGroup, id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Get PUSH frames
    frames = group.frames
    frames = [frame for frame in frames if frame.type == FrameType.PUSH]

    if not len(frames):
        return []

    frame_returns = send_images_to_push_frames(session, frames)

    session.commit()
    session.close()

    return frame_returns


@router.post("/{id}/prompts", response_model=list[Prompt])
def get_prompts(id: uuid.UUID, session: Session = Depends(get_session)):

    group = session.get(FrameGroup, id)

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    prompts = get_group_prompts(session, group)

    session.close()

    return prompts


@router.post("/{id}/prompts/rotate", response_model=list[PromptId])
def rotate_prompts(id: uuid.UUID, session: Session = Depends(get_session)):

    group = session.get(FrameGroup, id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    prompts = rotate_prompt_for_group(session, group)

    session.commit()
    session.close()

    return prompts
