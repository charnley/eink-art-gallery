import logging

from canvasserver.models.content import Image, Prompt, Prompts
from canvasserver.models.db import get_session
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

prefix = "/actions"
endpoint_queue = "/queue.png"

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
