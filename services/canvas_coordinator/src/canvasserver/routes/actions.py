import logging

from canvasserver.jobs import refresh_active_prompt, send_images_to_push_devices
from canvasserver.jobs.apis import send_image_to_device
from canvasserver.models.db import get_session
from canvasserver.models.db_models import Frame, Image, Prompt
from canvasserver.models.schemas import Frames, Prompts, PromptStatus, PromptStatusResponse
from fastapi import APIRouter, Depends, HTTPException
from shared_matplotlib_utils import get_basic_wifi
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

prefix = "/actions"

router = APIRouter(prefix=prefix, tags=["actions"])


# @router.get("/clean_up", response_model=None, tags=["actions"])
# def _clean_up(session: Session = Depends(get_session)):
#     # TODO Check if prompts are irrelevant, life time etc
#     raise NotImplementedError()


@router.get("/prompts_check", response_model=PromptStatusResponse, tags=["actions"])
def _check_prompts(session: Session = Depends(get_session)):

    query = session.execute(
        select(Prompt, func.count(Image.id))
        .outerjoin(Image, Image.prompt == Prompt.id)
        .group_by(Prompt.id)
        .having(func.count(Image.id) < Prompt.min_images)
    )

    results = query.all()

    prompt_statues = []

    for res in results:
        prompt = res[0]
        count = res[1]
        status = PromptStatus(image_count=count, **prompt.__dict__)
        prompt_statues.append(status)

    session.close()

    return PromptStatusResponse(prompts=prompt_statues, count=len(prompt_statues))


@router.get("/theme_check", response_model=None, tags=["actions"])
def _check_themes(session: Session = Depends(get_session)):
    raise NotImplementedError()


@router.get("/prompts_active", response_model=Prompts, tags=["actions"])
def refresh_active_prompts(session: Session = Depends(get_session)):

    # TODO Set manual active prompt

    prompt = refresh_active_prompt(session)

    if prompt is None:
        raise HTTPException(status_code=404, detail="No prompt setting is possible")

    prompts = [prompt]

    session.close()

    return Prompts(prompts=prompts, count=len(prompts))


# @router.get("/refresh_queues", response_model=None, tags=["actions"])
# def _refresh_active_prompts_in_queue(session: Session = Depends(get_session)):
#     raise NotImplementedError


@router.get("/update_push_devices", response_model=Frames, tags=["actions"])
def _refresh_push_screens(session: Session = Depends(get_session)):
    pushFrames = send_images_to_push_devices(session)

    logger.info(f"Updated {pushFrames}")

    session.commit()
    session.close()

    return pushFrames


@router.get("/send_wifi", response_model=Frame, tags=["actions"])
def _send_wifi(
    wifi_name: str, wifi_password: str, wifi_type: str, session: Session = Depends(get_session)
):

    # TODO Need to specify specific Frame to send it too
    # TODO Only works for PushFrame

    pushFrame = session.query(Frame).first()

    image = get_basic_wifi(wifi_name, wifi_password, wifi_type=wifi_type)

    send_image_to_device(image, pushFrame.model, pushFrame.endpoint)

    logger.info(f"Updated {pushFrame}")

    session.commit()
    session.close()

    return pushFrame
