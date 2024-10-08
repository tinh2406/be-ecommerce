from rest_framework.serializers import (
    CharField,
    DictField,
    ListField,
    ModelSerializer,
    ValidationError,
)

from items.models import Item
from items.services import CategoryService, ItemService

from ..utils.representation_item import representation_item
from .attribute_serializer import AttributeSerializer


class ItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "deleted_at", "category")

    category_id = CharField(max_length=255)
    images = ListField(child=CharField(max_length=255), required=False)
    attributes = AttributeSerializer(many=True, required=False)
    variants = ListField(child=DictField(), required=False)

    def validate(self, attrs):

        CategoryService.get(attrs.get("category_id"), raise_exception=True)
        # Kiểm tra xem có attributes không
        if "attributes" in attrs:
            # Nếu có attributes thì phải có variants ( variant đại diện cho giá của các tổ hợp thuộc tính)
            # Ví dụ size: [S, M] và color: [red, blue] thì sẽ có 4 variants
            if "variants" not in attrs:
                raise ValidationError({"variants": "This field is required"})

            # Lấy danh sách tên của các thuộc tính
            # Ví dụ: ["size", "color"]
            attribute_names = [attribute["name"] for attribute in attrs["attributes"]]

            # Lấy dictionary value của các thuộc tính
            # Ví dụ: {"size": {"S", "M"}, "color": {"red", "blue"}}
            attribute_values = {
                attribute["name"]: set(attribute["values"])
                for attribute in attrs["attributes"]
            }

            # Tính số lượng variants cần có
            # Ví dụ: size: [S, M] và color: [red, blue] thì sẽ có 1*2*2 = 4 variants
            total_variants = 1
            for attribute in attrs["attributes"]:
                total_variants *= len(attribute["values"])

            # Kiểm tra xem số lượng variants đã nhập vào có đủ không
            variant_dict = dict()  # Dùng dict để kiểm tra xem có trùng variants không
            for variant in attrs["variants"]:
                variant_key = ""
                for attribute_name in attribute_names:
                    if (
                        attribute_name not in variant
                    ):  # Kiểm tra xem variant có thiếu attribute không
                        raise ValidationError(
                            {attribute_name: "This field is required"}
                        )

                    variant_value = variant[attribute_name]  # Lấy giá trị của attribute
                    # Kiểm tra xem giá trị của attribute có hợp lệ không
                    if variant_value not in attribute_values[attribute_name]:
                        raise ValidationError(
                            {attribute_name: "This value is not valid"}
                        )
                    variant_key += f"{variant_value}|"  # Tạo key cho variant

                variant_dict[variant_key] = (
                    variant  # Ví dụ key: "S|red|", "M|red|", "S|blue|", "M|blue|"
                )

                # Kiểm tra các thuộc tính cần thiết
                if "price" not in variant:
                    raise ValidationError({"price": "This field is required"})
                if "image" not in variant:
                    raise ValidationError({"image": "This field is required"})

            # Kiểm tra xem số lượng variants đã nhập vào có đủ không
            if len(variant_dict) != total_variants:
                raise ValidationError(
                    {"variants": "The number of variants is not enough"}
                )
            attrs["variants"] = list(variant_dict.values())

        return attrs

    def to_representation(self, instance: Item):
        return representation_item(instance)

    def create(self, validated_data):
        item = ItemService.create(validated_data)
        return item

    def update(self, instance, validated_data):
        item = ItemService.update(instance, validated_data)
        return item
