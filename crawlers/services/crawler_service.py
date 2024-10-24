import json
from typing import Union

from django_celery_beat.models import CrontabSchedule, PeriodicTask


class CrawlerService:

    @classmethod
    def create(cls, validated: dict) -> PeriodicTask:

        name = validated.get("name")
        url = validated.get("url")
        quantity = validated.get("quantity")
        start_time = validated.get("start_time")
        end_time = validated.get("end_time")
        cycle_length = validated.get("cycle_length")

        request_params_id = validated.get("request_params_id")
        products_mapper_id = validated.get("products_mapper_id")
        product_mapper_id = validated.get("product_mapper_id")

        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=f"*/{cycle_length}",
        )

        task = PeriodicTask.objects.create(
            crontab=schedule,
            name=name,
            enabled=False,
            task="crawl_task",
            kwargs=json.dumps(
                {
                    "url": url,
                    "quantity": quantity,
                    "request_params_id": request_params_id,
                    "product_mapper_id": product_mapper_id,
                    "products_mapper_id": products_mapper_id,
                }
            ),
            expires=end_time,
            start_time=start_time,
        )

        return task

    @classmethod
    def get(cls, pk, raise_exception=True) -> Union["PeriodicTask", None]:
        try:
            crawler = PeriodicTask.objects.get(id=pk)
            return crawler
        except PeriodicTask.DoesNotExist:
            if raise_exception:
                raise PeriodicTask.DoesNotExist
            return None

    @classmethod
    def update(cls, instance: PeriodicTask, validated: dict) -> PeriodicTask:

        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute={validated.get("cycle_length")},
        )
        instance.crontab = schedule
        instance.name = validated.get("name")
        instance.enabled = False
        instance.task = "crawl_task"
        instance.kwargs = json.dumps(
            {
                "url": validated.get("url"),
                "quantity": validated.get("quantity"),
                "request_params_id": validated.get("request_params_id"),
                "product_mapper_id": validated.get("product_mapper_id"),
                "products_mapper_id": validated.get("products_mapper_id"),
            }
        )
        instance.expires = validated.get("end_time")
        instance.start_time = validated.get("start_time")
        instance.save()
        return instance

    @classmethod
    def activate_task(cls, pk):
        instance = cls.get(pk)
        instance.enabled = True
        instance.save()
        return True

    @classmethod
    def deactivate_task(cls, pk):
        instance = cls.get(pk)
        instance.enabled = False
        instance.save()
        return True

    @classmethod
    def delete(cls, pk):
        instance = cls.get(pk)
        instance.delete()
        return True
