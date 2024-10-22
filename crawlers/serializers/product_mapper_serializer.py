from rest_framework.serializers import (
    BooleanField,
    ChoiceField,
    DateTimeField,
    JSONField,
    ModelSerializer,
)

from core.utils import BaseQuerySerializer
from crawlers.constants import MapperOrderChoice
from crawlers.models import ProductMapper
from crawlers.services import ProductMapperService


class ProductMapperSerializer(ModelSerializer):

    properties = JSONField(default=dict)

    class Meta:
        model = ProductMapper
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        mapper = ProductMapperService.create(validated_data)
        return mapper.id

    def update(self, instance, validated_data):
        mapper = ProductMapperService.update(instance, validated_data)
        return mapper.id


class SimpleProductMapperSerializer(ModelSerializer):
    class Meta:
        model = ProductMapper
        fields = "__all__"


class QueryProductMapperSerializer(BaseQuerySerializer):
    is_deleted = BooleanField(allow_null=True, required=False)
    delete_from = DateTimeField(allow_null=True, required=False)
    delete_to = DateTimeField(allow_null=True, required=False)
    created_from = DateTimeField(allow_null=True, required=False)
    created_to = DateTimeField(allow_null=True, required=False)

    # override
    order_by = ChoiceField(allow_null=True, required=False, choices=MapperOrderChoice)
