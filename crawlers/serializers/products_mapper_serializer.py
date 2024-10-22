from rest_framework.serializers import ModelSerializer

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
