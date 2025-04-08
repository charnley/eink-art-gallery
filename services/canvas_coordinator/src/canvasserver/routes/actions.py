import logging

from canvasserver.jobs import refresh_active_prompt, send_images_to_push_devices
from canvasserver.models.content import Image, Prompt, Prompts, PushFrames
from canvasserver.models.db import get_session
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

prefix = "/actions"

router = APIRouter(prefix=prefix, tags=["actions"])


@router.get("/clean_up", response_model=None, tags=["actions"])
def _clean_up(session: Session = Depends(get_session)):
    # TODO Check if prompts needs to be updated
    # TODO Check if prompts are irrelevant
    return


@router.get("/prompts_check", response_model=Prompts, tags=["actions"])
def _check_prompts(session: Session = Depends(get_session)):

    MIN_IMAGES = 5
    query = (
        session.query(Prompt)
        .outerjoin(Image, Image.prompt == Prompt.id)
        .group_by(Prompt.id)
        .having(func.count(Image.id) < MIN_IMAGES)
    )
    prompts = query.all()
    return Prompts(prompts=prompts, count=len(prompts))


@router.get("/theme_check", response_model=None, tags=["actions"])
def _check_themes(session: Session = Depends(get_session)):
    return Response()


@router.get("/prompts_active", response_model=Prompts, tags=["actions"])
def refresh_active_prompts(session: Session = Depends(get_session)):

    # TODO Set manual active prompt

    prompt = refresh_active_prompt(session)

    if prompt is None:
        raise HTTPException(status_code=404, detail="No prompt setting is possible")

    prompts = [prompt]

    return Prompts(prompts=prompts, count=len(prompts))


@router.get("/refresh_queues", response_model=None, tags=["actions"])
def _refresh_active_prompts_in_queue(session: Session = Depends(get_session)):

    raise NotImplementedError


@router.get("/update_push_devices", response_model=PushFrames, tags=["actions"])
def _refresh_push_screens(session: Session = Depends(get_session)):
    pushFrames = send_images_to_push_devices(session)
    session.close()
    return pushFrames
