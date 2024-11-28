from rest_framework.serializers import (
    BooleanField,
    ChoiceField,
    DateTimeField,
    ModelSerializer,
    ValidationError,
)

from core.utils import BaseQuerySerializer
from crawlers.constants import MapperOrderChoice
from crawlers.models import ProductMapper


class ProductMapperSerializer(ModelSerializer):
    class Meta:
        model = ProductMapper
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):

        fields = [
            "attribute_name",
            "attribute_code",
            "attribute_values",
            "variant_price",
            "variant_image",
        ]

        missing_fields = [field for field in fields if not attrs.get(field)]

        if attrs.get("attributes") and attrs.get("variants") and missing_fields:
            raise ValidationError("Missing required fields for attributes or variants")
        return attrs


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
