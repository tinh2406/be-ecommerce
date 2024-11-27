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
from crawlers.constants import CrawlerOrderChoice, ScheduleChoice
from crawlers.services import CrawlerService, RequestParamsService
from crawlers.tasks.crawl_task import test_crawl_config


class ParamsSerializer(Serializer):
    take_key = CharField(max_length=255)
    page_key = CharField(max_length=255)

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        return {**data, **ret}

    def validate(self, attrs: dict):

        take_key = attrs["take_key"]
        page_key = attrs["page_key"]
        if not attrs.get(take_key):
            raise ValidationError({take_key: "This field is required."})
        if not attrs.get(page_key):
            raise ValidationError({page_key: "This field is required."})

        take = attrs[take_key]
        page = attrs[page_key]

        if not isinstance(take, int) or take < 1 or take > 100:
            raise ValidationError(
                {take_key: "This field must be an integer between 1 and 100."}
            )
        if not isinstance(page, int) or page < 1:
            raise ValidationError(
                {page_key: "This field must be an integer greater than 0."}
            )

        return attrs


class CrawlerSerializer(Serializer):

    name = CharField(max_length=255)
    url = CharField(max_length=255)
    detail_url = CharField(max_length=255)
    quantity = IntegerField(min_value=1)
    start_time = DateTimeField()
    end_time = DateTimeField()
    cycle_length = IntegerField(min_value=1, required=False)
    every = ChoiceField(choices=ScheduleChoice.CHOICES, required=False)

    product_mapper_id = CharField(max_length=255)
    products_mapper_id = CharField(max_length=255)

    headers = DictField()
    params = ParamsSerializer()

    def validate(self, attrs: dict):
        if attrs["start_time"] > attrs["end_time"]:
            raise ValidationError(
                {"end_time": "end_time must be greater than start_time"}
            )

        if attrs.get("cycle_length") and attrs.get("every"):
            raise ValidationError(
                {"cycle_length": "cycle_length and every can not be used together"}
            )
        if not attrs.get("cycle_length") and not attrs.get("every"):
            raise ValidationError({"cycle_length": "cycle_length or every is required"})

        try:
            test_crawl_config(**attrs)
        except Exception as e:
            raise ValidationError({"test_crawl_config": str(e)})

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
        ret = super().to_representation(instance)
        ret["crontab_id"] = instance.crontab_id
        if instance.crontab_id:
            ret["crontab"] = {
                "minute": instance.crontab.minute,
                "hour": instance.crontab.hour,
                "day_of_month": instance.crontab.day_of_month,
                "month_of_year": instance.crontab.month_of_year,
            }
        if instance.interval_id:
            ret["interval"] = {
                "every": instance.interval.every,
                "period": instance.interval.period,
            }
        return ret


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
            "interval": (
                {
                    "every": instance.interval.every,
                    "period": instance.interval.period,
                }
                if instance.interval_id
                else None
            ),
            "crontab": (
                {
                    "minute": instance.crontab.minute,
                    "hour": instance.crontab.hour,
                    "day_of_month": instance.crontab.day_of_month,
                    "month_of_year": instance.crontab.month_of_year,
                }
                if instance.crontab_id
                else None
            ),
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
