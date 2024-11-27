from rest_framework.serializers import (
    BooleanField,
    CharField,
    ChoiceField,
    DateTimeField,
    ModelSerializer,
)

from core.utils import BaseQuerySerializer
from products.constants import CategoryOrderChoice
from products.models import Category
from products.services import CategoryService


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ("id", "created_at", "deleted_at")

    parent_id = CharField(max_length=255, required=False, allow_null=True)

    def validate(self, attrs):
        parent_id = attrs.get("parent_id")
        if parent_id:
            CategoryService.get(parent_id, raise_exception=True)
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.parent_id:
            parent = CategoryService.get(instance.parent_id)
            data["parent"] = parent.name
        return data

    def create(self, validated_data):
        category = CategoryService.create(validated_data)
        return category

    def update(self, instance, validated_data):
        partial = validated_data.pop("partial", False)
        instance = CategoryService.update(instance, validated_data, partial=partial)
        return instance


class QueryCategorySerializer(BaseQuerySerializer):
    parent_id = (CharField(allow_blank=True, allow_null=True, required=False),)

    is_deleted = BooleanField(allow_null=True, required=False)
    is_all = BooleanField(allow_null=True, required=False)
    delete_from = DateTimeField(allow_null=True, required=False)
    delete_to = DateTimeField(allow_null=True, required=False)
    created_from = DateTimeField(allow_null=True, required=False)
    created_to = DateTimeField(allow_null=True, required=False)

    # override
    order_by = ChoiceField(allow_null=True, required=False, choices=CategoryOrderChoice)
