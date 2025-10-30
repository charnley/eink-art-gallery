import datetime
import logging

from canvasserver.models.db import get_session
from canvasserver.models.db_models import Frame, FrameGroup
from canvasserver.models.schemas import FrameGroupWithFrames, FrameUpdateNoGroup
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

prefix = "/system"

router = APIRouter(prefix=prefix, tags=["system"])


@router.get("/get-time", response_model=int, tags=["system"])
def get_time():
    now = datetime.datetime.now()
    return int(now.timestamp())


@router.get("/export/groups", response_model=list[FrameGroupWithFrames], tags=["system"])
def get_groups(session: Session = Depends(get_session)):

    groups = session.query(FrameGroup).all()
    groups_frames = []

    for group in groups:

        groups_frames.append(
            FrameGroupWithFrames(
                **group.model_dump(),
                frames=[FrameUpdateNoGroup(**frame.model_dump()) for frame in group.frames]
            )
        )

    session.close()

    return groups_frames


@router.post("/import/groups", response_model=list[FrameGroup], tags=["system"])
def set_groups(
    update_groups: list[FrameGroupWithFrames],
    session: Session = Depends(get_session),
):

    groups = []

    for update_group in update_groups:

        update_frames = update_group.frames
        data = update_group.model_dump()
        del data["frames"]

        group = FrameGroup(**data)
        groups.append(group)
        session.add(group)

        if update_frames is None:
            continue

        for update_frame in update_frames:
            frame = Frame(**update_frame.model_dump())
            frame.group_id = group.id
            session.add(frame)

    session.commit()
    session.close()

    return groups
