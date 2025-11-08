import datetime

import numpy as np
from apscheduler.triggers.cron import CronTrigger

BUFFER_PERCENT = 0.1  # 10%
MIN_BUFFER = 30  # seconds


def get_schedule_datetimes(cron_string, count=10) -> list[datetime.datetime]:

    schedule: list[datetime.datetime] = []

    now = datetime.datetime.now()
    timezone = now.tzinfo

    trigger = CronTrigger.from_crontab(cron_string)
    trigger.timezone = timezone

    next_datetime = trigger.get_next_fire_time(None, now)
    assert next_datetime is not None

    for _ in range(count - 1):
        next_datetime = trigger.get_next_fire_time(
            None, next_datetime + datetime.timedelta(seconds=1)
        )
        assert next_datetime is not None
        schedule.append(next_datetime)

    return schedule


def get_seconds_until_next(cron_string: str) -> int:
    """
    e.g. cron_string = "30 4 * * *"

    Note, DeepSleep devices like ESP32 has a tendency to have % error,
    so the longer it sleeps the more inaccurate it becomes.
    A time buffer is needed so it doesn't wake up minutes before CRON,
    and then wakes up an additional time.

    """

    # TODO Test if fetch at the exact same time as cron

    now = datetime.datetime.now()
    timezone = now.tzinfo

    trigger = CronTrigger.from_crontab(cron_string)
    trigger.timezone = timezone

    next_datetime = trigger.get_next_fire_time(None, now)
    assert next_datetime is not None, "Wrong cron format"

    delta = next_datetime - now
    nextnext_datetime = trigger.get_next_fire_time(
        None, now + delta + datetime.timedelta(seconds=1)
    )
    assert nextnext_datetime is not None

    interval = (nextnext_datetime - next_datetime).total_seconds()
    buffer_seconds = max(MIN_BUFFER, np.ceil(interval * BUFFER_PERCENT))

    if (next_datetime - now).total_seconds() < buffer_seconds:
        target_datetime = nextnext_datetime
    else:
        target_datetime = next_datetime

    seconds = np.ceil((target_datetime - now).total_seconds())

    return seconds
