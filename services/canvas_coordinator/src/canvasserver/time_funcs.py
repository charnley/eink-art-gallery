import datetime

import numpy as np
from apscheduler.triggers.cron import CronTrigger

BUFFER_PERCENT = 0.1  # 10%
MIN_BUFFER = 30  # seconds


def get_schedule_datetimes(cron_string, count=10) -> list[datetime.datetime]:

    schedule: list[datetime.datetime] = []

    local_tz = datetime.datetime.now().astimezone().tzinfo
    now = datetime.datetime.now(tz=local_tz)

    trigger = CronTrigger.from_crontab(cron_string, timezone=local_tz)

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

    local_tz = datetime.datetime.now().astimezone().tzinfo
    now = datetime.datetime.now(tz=local_tz)

    trigger = CronTrigger.from_crontab(cron_string, timezone=local_tz)

    next_datetime = trigger.get_next_fire_time(None, now)
    assert next_datetime is not None, "Wrong cron format"
    assert now.tzinfo == next_datetime.tzinfo

    delta = next_datetime - now

    nextnext_datetime = trigger.get_next_fire_time(
        None, now + delta + datetime.timedelta(seconds=1)
    )
    assert nextnext_datetime is not None

    interval = (nextnext_datetime - next_datetime).total_seconds()
    buffer_seconds = max(MIN_BUFFER, np.ceil(interval * BUFFER_PERCENT))
    is_early = (next_datetime - now).total_seconds() < buffer_seconds

    target_datetime = nextnext_datetime if is_early else next_datetime

    seconds = np.ceil((target_datetime - now).total_seconds())

    return seconds
