import json

from django_celery_beat.models import PeriodicTask
from rest_framework.fields import DictField
from rest_framework.serializers import (
    BooleanField,
    CharField,
    ChoiceField,
    DateTimeField,
    IntegerField,
    ModelSerializer,
    Serializer,
    ValidationError,
)

from core.utils import BaseQuerySerializer
from crawlers.constants import CrawlerOrderChoice
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

        params = attrs.get("params")
        take_key = params.get("take_key")
        page_key = params.get("page_key")
        if not take_key:
            raise ValidationError({"params": "take_key is required"})
        if not page_key:
            raise ValidationError({"params": "page_key is required"})
        take = params.get(take_key)
        page = params.get(page_key)
        if not take:
            raise ValidationError({"params": f"{take_key} is required"})
        if not page:
            raise ValidationError({"params": f"{page_key} is required"})

        try:
            test_crawl_config(**attrs)
        except Exception as e:
            raise ValidationError(e)

        return attrs

    def to_representation(self, instance):
        kwargs = json.loads(instance.kwargs)
        request_params = RequestParamsService.get(kwargs["request_params_id"])
        data = {
            "id": instance.id,
            "name": instance.name,
            "expires": instance.expires,
            "enabled": instance.enabled,
            "last_run_at": instance.last_run_at,
            "total_run_count": instance.total_run_count,
            "date_changed": instance.date_changed,
            "start_time": instance.start_time,
            "kwargs": kwargs,
            "params": request_params.params,
            "headers": request_params.headers,
        }
        return data

    def create(self, validated_data):
        try:
            crawler = CrawlerService.create(validated_data)
            return crawler.id
        except Exception as e:
            raise ValidationError(e)

    def update(self, instance, validated_data):
        try:
            crawler = CrawlerService.update(instance, validated_data)
            return crawler.id
        except Exception as e:
            raise ValidationError(e)


class SimpleCrawlerSerializer(ModelSerializer):
    class Meta:
        model = PeriodicTask
        fields = "__all__"

    def to_representation(self, instance: PeriodicTask):
        instance.kwargs = json.loads(instance.kwargs)
        return super().to_representation(instance)


class QueryCrawlerSerializer(BaseQuerySerializer):

    is_deleted = BooleanField(allow_null=True, required=False)
    delete_from = DateTimeField(allow_null=True, required=False)
    delete_to = DateTimeField(allow_null=True, required=False)
    created_from = DateTimeField(allow_null=True, required=False)
    created_to = DateTimeField(allow_null=True, required=False)
    is_running = BooleanField(allow_null=True, required=False)
    last_run_from = DateTimeField(allow_null=True, required=False)
    last_run_to = DateTimeField(allow_null=True, required=False)
    circle_time_from = IntegerField(allow_null=True, required=False)
    circle_time_to = IntegerField(allow_null=True, required=False)

    # override
    order_by = ChoiceField(allow_null=True, required=False, choices=CrawlerOrderChoice)
