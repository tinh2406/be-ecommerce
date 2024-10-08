from rest_framework.serializers import ModelSerializer

from items.models import Category


class SimpleCategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.name,
            "parent_id": instance.parent_id,
            "created_at": instance.created_at,
            "deleted_at": instance.deleted_at,
        }
