import logging
from functools import partial

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from canvasserver.jobs.push_device_logic import send_images_to_push_frames
from canvasserver.models.db_models import FrameGroup
from canvasserver.models.queries import rotate_prompt_for_group
from shared_constants import FrameType
from sqlalchemy import select

from .models.db import session_scope

logger = logging.getLogger(__name__)

JOB_PROMPT = "update-prompts"
JOB_FRAME = "push-frames"


def is_valid_cron(cron):

    try:
        _ = CronTrigger.from_crontab(cron)
    except Exception:
        return False

    return True


def update_group_prompts(group_id):

    with session_scope() as session:

        group = session.get(FrameGroup, group_id)

        if group is None:
            logger.warning(f"Group {group_id} no longer exists, skipping")
            return

        _ = rotate_prompt_for_group(session, group)

        session.commit()


def refresh_group_images(group_id):

    logger.warning(f"Refreshing {group_id}")

    with session_scope() as session:

        group = session.get(FrameGroup, group_id)

        if group is None:
            logger.warning(f"Group {group_id} no longer exists, skipping")
            return []

        logger.info(f"Updating: {group}")

        # Collect all Push Frames
        frames = group.frames
        frames = [frame for frame in frames if frame.type == FrameType.PUSH]

        if not len(frames):
            return []

        frame_statuses = send_images_to_push_frames(session, frames)

        for frame_status in frame_statuses:
            if frame_status.status_code != 200:
                logger.error(f"Unable to push: {frame_status}")
                continue

            logger.info(f"Able to push: {frame_status}")

        session.commit()


def _job_id(kind, group_id):
    return f"{kind}:{group_id}"


def _sync_job(scheduler, job_id, func, cron, name):
    """Make job `job_id` match `cron`. A missing or invalid cron removes the job."""

    existing = scheduler.get_job(job_id)

    if cron is None or not is_valid_cron(cron):
        if existing is not None:
            scheduler.remove_job(job_id)
        return

    trigger = CronTrigger.from_crontab(cron)

    if existing is not None and str(existing.trigger) == str(trigger):
        return

    if existing is not None:
        scheduler.remove_job(job_id)

    scheduler.add_job(func, trigger, id=job_id, name=name)


def sync_group_crons(scheduler, session):
    """Add, reschedule or remove jobs so the scheduler matches the database."""

    groups = session.exec(select(FrameGroup)).all()
    wanted = set()

    for (group,) in groups:

        prompt_id = _job_id(JOB_PROMPT, group.id)
        frame_id = _job_id(JOB_FRAME, group.id)
        wanted.update([prompt_id, frame_id])

        _sync_job(
            scheduler,
            prompt_id,
            partial(update_group_prompts, group.id),
            group.schedule_prompt,
            f"update-prompts ({group.name}, cron={group.schedule_prompt})",
        )

        # Push frames are checked when the job runs, so later additions are included
        _sync_job(
            scheduler,
            frame_id,
            partial(refresh_group_images, group.id),
            group.schedule_frame,
            f"push-frames ({group.name}, cron={group.schedule_frame})",
        )

    # Remove jobs of deleted groups
    prefixes = (f"{JOB_PROMPT}:", f"{JOB_FRAME}:")
    for job in scheduler.get_jobs():
        if job.id.startswith(prefixes) and job.id not in wanted:
            scheduler.remove_job(job.id)

    logger.info(f"Scheduled jobs: {[job.name for job in scheduler.get_jobs()]}")


def create_scheduler(session):
    scheduler = BackgroundScheduler()
    sync_group_crons(scheduler, session)
    return scheduler


def reload_crons(app):
    """Re-sync the app's scheduler with the database. Returns None if no scheduler runs."""

    scheduler = getattr(app.state, "scheduler", None)

    if scheduler is None:
        return None

    with session_scope() as session:
        sync_group_crons(scheduler, session)

    return len(scheduler.get_jobs())
