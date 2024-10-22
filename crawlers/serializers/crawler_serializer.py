import json

from django_celery_beat.models import PeriodicTask
from rest_framework.fields import DictField
from rest_framework.serializers import (
    CharField,
    DateTimeField,
    IntegerField,
    Serializer,
    ValidationError,
)

from crawlers.services import CrawlerService, RequestParamsService
from crawlers.tasks.crawl_task import test_crawl_config


class CrawlerSerializer(Serializer):

    name = CharField(max_length=255)
    url = CharField(max_length=255)
    quantity = IntegerField()
    start_time = DateTimeField()
    end_time = DateTimeField()
    cycle_length = IntegerField()

    product_mapper_id = CharField(max_length=255)
    products_mapper_id = CharField(max_length=255)

    headers = DictField()
    params = DictField()

    class Meta:
        model = PeriodicTask
        fields = [
            "id",
            "name",
            "expires",
            "enabled",
            "last_run_at",
            "total_run_count",
            "date_changed",
            "start_time",
            "kwargs",
        ]
        read_only_fields = [
            "id",
            "expires",
            "enabled",
            "last_run_at",
            "total_run_count",
            "date_changed",
            "start_time",
            "kwargs",
        ]
        write_only_fields = [
            "url",
            "quantity",
            "start_time",
            "end_time",
            "cycle_length",
            "product_mapper_id",
            "products_mapper_id",
        ]

    def validate(self, attrs: dict):
        if (
            attrs.get("start_time") is not None
            and attrs.get("end_time") is not None
            and str(attrs.get("start_time")) > str(attrs.get("end_time"))
        ):
            raise ValidationError(
                {"end_time": "end_time must be greater than start_time"}
            )
        if int(attrs.get("cycle_length") or 60) < 0:
            raise ValidationError(
                {"cycle_length": "cycle_length must be greater than 0"}
            )
        if int(attrs.get("quantity") or 10) < 0:
            raise ValidationError({"quantity": "quantity must be greater than 0"})

        request_params = RequestParamsService.create(attrs)
        attrs["request_params_id"] = str(request_params.id)

        try:
            test_crawl_config(**attrs)
        except Exception as e:
            raise ValidationError(e)

        return attrs

    def to_representation(self, instance):
        data = {
            "id": instance.id,
            "name": instance.name,
            "expires": instance.expires,
            "enabled": instance.enabled,
            "last_run_at": instance.last_run_at,
            "total_run_count": instance.total_run_count,
            "date_changed": instance.date_changed,
            "start_time": instance.start_time,
            "kwargs": json.loads(instance.kwargs),
        }
        return data

    def create(self, validated_data):
        try:
            crawler = CrawlerService.create(validated_data)
            return crawler.id
        except Exception as e:
            raise ValidationError(e)
