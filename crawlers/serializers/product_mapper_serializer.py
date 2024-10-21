from rest_framework.serializers import JSONField, ModelSerializer

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
