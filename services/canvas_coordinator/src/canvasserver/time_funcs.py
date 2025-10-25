import datetime

from apscheduler.triggers.cron import CronTrigger


def get_seconds_until_next(cron_string):
    """
    e.g. cron_string = "30 4 * * *"
    """

    now = datetime.datetime.now()
    timezone = now.tzinfo

    trigger = CronTrigger.from_crontab(cron_string)
    trigger.timezone = timezone
    next_datetime = trigger.get_next_fire_time(None, now)

    assert next_datetime is not None, "Wrong cron format"

    delta = next_datetime - now

    seconds = int(delta.total_seconds())

    return seconds
