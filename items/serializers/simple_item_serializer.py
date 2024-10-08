from rest_framework.serializers import ModelSerializer

from items.models import Item


class SimpleItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["category_id"] = instance.category.id
        return ret
