import json
from typing import Union

from django_celery_beat.models import PeriodicTask
from rest_framework.exceptions import NotFound

from crawlers.services.request_params_service import RequestParamsService
from crawlers.utils import periodic_task_cron_builder


class CrawlerService:

    @classmethod
    def create(cls, validated: dict) -> PeriodicTask:

        name = validated.get("name")
        url = validated.get("url")
        quantity = validated.get("quantity")
        start_time = validated.get("start_time")
        end_time = validated.get("end_time")
        cycle_length = validated.get("cycle_length")
        every = validated.get("every")
        products_mapper_id = validated.get("products_mapper_id")
        product_mapper_id = validated.get("product_mapper_id")

        schedule = periodic_task_cron_builder(every, cycle_length, start_time)

        request_params = RequestParamsService.create(validated)
        request_params_id = str(request_params.id)

        task = PeriodicTask.objects.create(
            **schedule,
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
                raise NotFound("Crawler not found")
            return None

    @classmethod
    def update(cls, instance: PeriodicTask, validated: dict) -> PeriodicTask:

        start_time = validated.get("start_time")
        end_time = validated.get("end_time")
        cycle_length = validated.get("cycle_length")
        every = validated.get("every")
        schedule = periodic_task_cron_builder(every, cycle_length, start_time)

        instance.crontab = schedule.get("crontab")
        instance.interval = schedule.get("interval")
        instance.name = validated.get("name")
        instance.expires = end_time
        instance.start_time = start_time

        kwargs = json.loads(instance.kwargs)
        kwargs["quantity"] = validated.get("quantity")
        instance.kwargs = json.dumps(kwargs)

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

    @classmethod
    def search(cls, query_params: dict, paginate=True, **kwargs):

        query_set = PeriodicTask.objects.all()

        # Lấy các tham số truy vấn
        keyword = query_params.get("keyword")
        is_running = query_params.get("is_running")
        last_run_from = query_params.get("last_run_from")
        last_run_to = query_params.get("last_run_to")
        order_by = query_params.get("order_by") or "last_run_at"
        order_type = query_params.get("order_type") or "desc"
        page_size = query_params.get("page_size") or 10
        page = query_params.get("page") or 1
        skip = (page - 1) * page_size  # Tính toán skip từ page và page_size

        if is_running is not None:
            query_set = query_set.filter(enabled=is_running)

        # Lọc theo các thuộc tính khác
        if keyword:
            query_set = query_set.filter(name__icontains=keyword)

        if last_run_from:
            query_set = query_set.filter(last_run_at__gte=last_run_from)
        if last_run_to:
            query_set = query_set.filter(last_run_at__lte=last_run_to)

        if paginate:
            total = query_set.count()
            query_set = query_set.order_by(
                f"{'-' if order_type == 'desc' else ''}{order_by}"
            )[skip : skip + page_size]

            meta = {
                "page_count": (total - 1) // page_size + 1,
                "item_count": total,
                "page_size": page_size,
                "page": page,
            }
            return query_set, meta

        return query_set
