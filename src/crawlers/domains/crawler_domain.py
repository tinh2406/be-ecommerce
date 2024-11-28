import json
from typing import Union

from django_celery_beat.models import PeriodicTask
from rest_framework.exceptions import NotFound

from crawlers.utils import periodic_task_cron_builder


class CrawlerDomain:

    @classmethod
    def create(cls, validated_crawler: dict) -> PeriodicTask:

        name = validated_crawler.get("name")
        url = validated_crawler.get("url")
        detail_url = validated_crawler.get("detail_url")
        quantity = validated_crawler.get("quantity")
        start_time = validated_crawler.get("start_time")
        end_time = validated_crawler.get("end_time")
        cycle_length = validated_crawler.get("cycle_length")
        every = validated_crawler.get("every")
        products_mapper_id = validated_crawler.get("products_mapper_id")
        product_mapper_id = validated_crawler.get("product_mapper_id")
        request_params_id = validated_crawler.get("request_params_id")

        schedule = periodic_task_cron_builder(every, cycle_length, start_time)

        task = PeriodicTask.objects.create(
            **schedule,
            name=name,
            enabled=False,
            task="crawl_task",
            kwargs=json.dumps(
                {
                    "url": url,
                    "detail_url": detail_url,
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
            crawler = PeriodicTask.objects.prefetch_related("interval", "crontab").get(
                id=pk
            )
            return crawler
        except PeriodicTask.DoesNotExist:
            if raise_exception:
                raise NotFound("Crawler not found")
            return None

    @classmethod
    def update(cls, instance: PeriodicTask, validated_crawler: dict) -> PeriodicTask:

        name = validated_crawler.get("name")
        url = validated_crawler.get("url")
        detail_url = validated_crawler.get("detail_url")
        quantity = validated_crawler.get("quantity")
        start_time = validated_crawler.get("start_time")
        end_time = validated_crawler.get("end_time")
        cycle_length = validated_crawler.get("cycle_length")
        every = validated_crawler.get("every")
        products_mapper_id = validated_crawler.get("products_mapper_id")
        product_mapper_id = validated_crawler.get("product_mapper_id")
        request_params_id = validated_crawler.get("request_params_id")

        schedule = periodic_task_cron_builder(every, cycle_length, start_time)

        instance.name = name
        instance.enabled = False
        instance.expires = end_time
        instance.start_time = start_time
        instance.crontab = schedule.get("crontab")
        instance.interval = schedule.get("interval")
        instance.kwargs = json.dumps(
            {
                "url": url,
                "detail_url": detail_url,
                "quantity": quantity,
                "request_params_id": request_params_id,
                "product_mapper_id": product_mapper_id,
                "products_mapper_id": products_mapper_id,
            }
        )

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

        query_set = PeriodicTask.objects.all().prefetch_related("crontab", "interval")

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

        query_set = query_set.filter(task="crawl_task")

        if is_running is not None:
            query_set = query_set.filter(enabled=is_running)

        # Lọc theo các thuộc tính khác
        if keyword:
            query_set = query_set.filter(name__icontains=keyword)

        if last_run_from:
            query_set = query_set.filter(last_run_at__gte=last_run_from)
        if last_run_to:
            query_set = query_set.filter(last_run_at__lte=last_run_to)

        query_set = query_set.order_by(
            f"{'-' if order_type == 'desc' else ''}{order_by}", "-total_run_count"
        )
        if paginate:
            total = query_set.count()
            query_set = query_set[skip : skip + page_size]

            meta = {
                "page_count": (total - 1) // page_size + 1,
                "item_count": total,
                "page_size": page_size,
                "page": page,
            }
            return query_set, meta

        return query_set
