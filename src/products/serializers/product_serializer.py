from typing import Any

from rest_framework.serializers import (
    BooleanField,
    CharField,
    ChoiceField,
    DateTimeField,
    DictField,
    ListField,
    ModelSerializer,
    Serializer,
    ValidationError,
)

from core.utils import BaseQuerySerializer
from products.constants import ProductOrderChoice
from products.models import Product
from products.services import CategoryService, ProductService

from .attribute_serializer import AttributeSerializer


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "deleted_at", "category")

    category_id = CharField(max_length=255)
    images = ListField(child=CharField(max_length=255), required=False)
    attributes = AttributeSerializer(many=True, required=False)
    variants = ListField(child=DictField(), required=False)

    def validate(self, attrs):
        CategoryService.get(attrs.get("category_id"), raise_exception=True)

        attributes = attrs.get("attributes")
        variants = attrs.get("variants")

        # Kiểm tra xem có attributes không
        if attributes:
            # Nếu có attributes thì phải có variants
            if not variants:
                raise ValidationError({"variants": "This field is required"})

            # Lấy danh sách tên của các thuộc tính và giá trị của chúng
            attribute_values, attribute_names = (
                self.extract_names_values_from_attributes(attributes)
            )

            # Tính tổng số variants cần có
            total_variants = 1
            for values in attribute_values.values():
                total_variants *= len(values)

            # Xử lý variants
            variants = self.validate_variant(
                variants, attribute_names, attribute_values
            )

            # Kiểm tra xem số lượng variants đã nhập vào có đủ không
            if len(variants) != total_variants:
                raise ValidationError(
                    {"variants": "The number of variants is not enough"}
                )
            attrs["variants"] = variants

        return attrs

    def to_representation(self, instance: Product):
        data: dict[str, Any] = dict()
        data["id"] = str(instance.id)
        data["name"] = instance.name
        data["description"] = instance.description
        data["price"] = instance.price
        data["hot_price"] = instance.hot_price
        data["thumbnail"] = instance.thumbnail
        data["created_at"] = instance.created_at
        data["updated_at"] = instance.updated_at
        data["deleted_at"] = instance.deleted_at
        data["category_id"] = instance.category_id
        data["category"] = instance.category.name

        images = [image.url for image in instance.images.all()]
        for variant in instance.variants.all():
            images.append(variant.image)
        data["images"] = images

        data["attributes"] = {
            attribute.name: [value.value for value in attribute.values.all()]
            for attribute in instance.attributes.all()
        }
        data["variants"] = [
            {
                "price": variant.price,
                "hot_price": variant.hot_price,
                "image": variant.image,
                "attributes": {
                    attribute.product_attribute_value.attribute.name: attribute.product_attribute_value.value
                    for attribute in variant.attributes.all()
                },
            }
            for variant in instance.variants.all()
        ]

        return data

    def create(self, validated_data):
        product = ProductService.create_product(validated_data)
        return product

    def update(self, instance, validated_data):
        product = ProductService.update(instance, validated_data)
        return product

    @staticmethod
    def extract_names_values_from_attributes(attributes):
        """ "
        Process attributes to extract names and values.
        Input: [{"name": "color", "values": ["red", "yellow"]}]
        Output: {"color": {"red", "yellow"}}, ["color",]
        """

        # Lấy danh sách tên của các thuộc tính và giá trị của chúng
        attribute_values = {
            attribute["name"]: set(attribute["values"]) for attribute in attributes
        }
        # Lấy danh sách tên của các thuộc tính
        attribute_names = list(attribute_values.keys())

        return attribute_values, attribute_names

    @staticmethod
    def validate_variant(variants, attribute_names, attribute_values):
        """Validate and process variants based on attribute names and values"""
        """Loại bỏ các giá trị không hợp lệ và kiểm tra các thuộc tính cần thiết"""
        variant_dict = {}
        for variant in variants:
            variant_key = []
            for attribute_name in attribute_names:
                variant_value = variant.get(attribute_name)

                if not (
                    variant_value and variant_value in attribute_values[attribute_name]
                ):
                    raise ValidationError({attribute_name: "This value is not valid"})
                variant_key.append(variant_value)

            variant_key = "|".join(variant_key)
            variant_dict[variant_key] = variant  # Dùng variant làm giá trị cho dict

            # Kiểm tra các thuộc tính cần thiết
            if "price" not in variant:
                raise ValidationError({"price": "This field is required"})
            if "image" not in variant:
                raise ValidationError({"image": "This field is required"})

        return list(variant_dict.values())


class QueryByListIds(Serializer):
    product_ids = ListField(child=CharField(max_length=255))


class QueryProductSerializer(BaseQuerySerializer):
    category_id = CharField(allow_blank=True, allow_null=True, required=False)

    is_deleted = BooleanField(allow_null=True, required=False)
    delete_from = DateTimeField(allow_null=True, required=False)
    delete_to = DateTimeField(allow_null=True, required=False)
    created_from = DateTimeField(allow_null=True, required=False)
    created_to = DateTimeField(allow_null=True, required=False)
    price_from = CharField(allow_null=True, required=False)
    price_to = CharField(allow_null=True, required=False)

    # override
    order_by = ChoiceField(allow_null=True, required=False, choices=ProductOrderChoice)
