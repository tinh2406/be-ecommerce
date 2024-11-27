from rest_framework.serializers import ModelSerializer

from products.models import Product


class SimpleProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["category_id"] = instance.category.id
        return ret
