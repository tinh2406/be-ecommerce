from rest_framework.serializers import (
    BooleanField,
    ChoiceField,
    DateTimeField,
    ModelSerializer,
)

from core.utils import BaseQuerySerializer
from crawlers.constants import MapperOrderChoice
from crawlers.models.products_mapper import ProductsMapper
from crawlers.services import ProductsMapperService


class ProductsMapperSerializer(ModelSerializer):

    class Meta:
        model = ProductsMapper
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        mapper = ProductsMapperService.create(validated_data)
        return mapper.id

    def update(self, instance, validated_data):
        mapper = ProductsMapperService.update(instance, validated_data)
        return mapper.id


class SimpleProductsMapperSerializer(ModelSerializer):
    class Meta:
        model = ProductsMapper
        fields = "__all__"


class QueryProductsMapperSerializer(BaseQuerySerializer):
    is_deleted = BooleanField(allow_null=True, required=False)
    delete_from = DateTimeField(allow_null=True, required=False)
    delete_to = DateTimeField(allow_null=True, required=False)
    created_from = DateTimeField(allow_null=True, required=False)
    created_to = DateTimeField(allow_null=True, required=False)

    # override
    order_by = ChoiceField(allow_null=True, required=False, choices=MapperOrderChoice)
