import re

from django_celery_beat.models import CrontabSchedule, IntervalSchedule

from crawlers.constants import ScheduleChoice


class NotFoundKeyException(Exception):
    pass


def get_value_by_nested_key(data, key, is_required=False):
    value = data
    if key is None:
        if is_required:
            raise NotFoundKeyException(f"Key {key} is required")
        return None
    for k in key.split("/"):
        value = value.get(k)
        if value is None and is_required:
            raise NotFoundKeyException(f"Key {k} is not valid")
    return value


def remove_html_tags(text=None):
    if text is None:
        return None
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def remove_tiki_text_extension(text=None):
    if text is None:
        return None
    text = text.split("Giá sản phẩm trên Tiki đã bao gồm thuế theo luật hiện hành.")[0]
    return text


def periodic_task_cron_builder(every, cycle_length, start_time):
    if cycle_length:
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=cycle_length,
            period=IntervalSchedule.MINUTES,
        )
        return {
            "interval": schedule,
        }
    if every == ScheduleChoice.MINUTE:
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="*/1",
        )
    elif every == ScheduleChoice.HOUR:
        schedule, _ = CrontabSchedule.objects.get_or_create(
            hour="*/1",
            minute=f"{start_time.minute}",
        )
    elif every == ScheduleChoice.DAY:
        schedule, _ = CrontabSchedule.objects.get_or_create(
            day_of_month="*/1",
            hour=f"{start_time.hour}",
            minute=f"{start_time.minute}",
        )
    elif every == ScheduleChoice.MONTH:
        schedule, _ = CrontabSchedule.objects.get_or_create(
            month_of_year="*/1",
            day_of_month=f"{start_time.day}",
            hour=f"{start_time.hour}",
            minute=f"{start_time.minute}",
        )
    else:
        schedule, _ = CrontabSchedule.objects.get_or_create(
            month_of_year=f"{start_time.month}",
            day_of_month=f"{start_time.day}",
            hour=f"{start_time.hour}",
            minute=f"{start_time.minute}",
        )

    return {
        "crontab": schedule,
    }
