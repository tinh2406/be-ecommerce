from rest_framework.serializers import ModelSerializer

from items.models import Item


class SimpleItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"
