import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from canvasserver.jobs.push_device_logic import send_images_to_push_frames
from canvasserver.models.db_models import FrameGroup
from canvasserver.models.queries import rotate_prompt_for_group
from shared_constants import FrameType
from sqlalchemy import select

from .models.db import get_session

logger = logging.getLogger(__name__)


def is_valid_cron(cron):

    try:
        _ = CronTrigger.from_crontab(cron)
    except Exception:
        return False

    return True


def update_group_prompts(group_id):

    session = get_session()

    group = session.get(FrameGroup, group_id)
    assert group is not None

    _ = rotate_prompt_for_group(session, group)

    session.commit()
    session.close()


def refresh_group_images(group_id):

    session = get_session()

    group = session.get(FrameGroup, group_id)
    assert group is not None

    # Collect all Push Frames
    frames = group.frames
    frames = [frame for frame in frames if frame.type == FrameType.PUSH]

    if not len(frames):
        session.close()
        return []

    frame_statuses = send_images_to_push_frames(frames, session)

    for frame_status in frame_statuses:
        if frame_status.status_code != 200:
            logger.error(f"Unable to push: {frame_status}")

    session.commit()
    session.close()


def has_push_frames(group):
    frames = group.frames
    frames = [frame for frame in frames if frame.type == FrameType.PUSH]
    return len(frames)


def attach_group_crons(session):

    scheduler = BackgroundScheduler()
    groups = session.exec(select(FrameGroup)).all()

    for results in groups:

        group = results[0]

        if group.schedule_prompt is not None and is_valid_cron(group.schedule_prompt):
            scheduler.add_job(
                lambda: update_group_prompts(group.id),
                CronTrigger.from_crontab(group.schedule_prompt),
            )

        if (
            group.schedule_frame is not None
            and is_valid_cron(group.schedule_frame)
            and has_push_frames(group)
        ):
            scheduler.add_job(
                lambda: refresh_group_images(group.id),
                CronTrigger.from_crontab(group.schedule_frame),
            )

    return scheduler
