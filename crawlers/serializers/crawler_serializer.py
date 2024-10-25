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


def validate_params(data: dict):
    if not data.get("take_key"):
        raise ValidationError({"take_key": "This field is required."})
    if not data.get("page_key"):
        raise ValidationError({"page_key": "This field is required."})

    take_key = data["take_key"]
    page_key = data["page_key"]
    if not data.get(take_key):
        raise ValidationError({take_key: "This field is required."})
    if not data.get(page_key):
        raise ValidationError({page_key: "This field is required."})

    take = data[take_key]
    page = data[page_key]

    if not isinstance(take, int) or take < 1 or take > 100:
        data[take_key] = 10
    if not isinstance(page, int) or page < 1:
        data[page_key] = 1

    return data


class CrawlerSerializer(Serializer):

    name = CharField(max_length=255)
    url = CharField(max_length=255)
    quantity = IntegerField(min_value=1)
    start_time = DateTimeField()
    end_time = DateTimeField()
    cycle_length = IntegerField(min_value=1)

    product_mapper_id = CharField(max_length=255)
    products_mapper_id = CharField(max_length=255)

    headers = DictField()
    params = DictField()

    def validate(self, attrs: dict):
        if attrs["start_time"] > attrs["end_time"]:
            raise ValidationError(
                {"end_time": "end_time must be greater than start_time"}
            )
        attrs["params"] = validate_params(attrs["params"])

        try:
            test_crawl_config(**attrs)
        except Exception as e:
            raise ValidationError(e)

        return attrs

    def create(self, validated_data):
        try:
            crawler = CrawlerService.create(validated_data)
            return crawler.id
        except Exception as e:
            raise ValidationError(e)


class PeriodicTaskSerializer(ModelSerializer):
    class Meta:
        model = PeriodicTask
        fields = "__all__"

    def to_representation(self, instance: PeriodicTask):
        instance.kwargs = json.loads(instance.kwargs)
        return super().to_representation(instance)


class DetailPeriodicTaskSerializer(ModelSerializer):
    class Meta:
        model = PeriodicTask
        fields = "__all__"

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
