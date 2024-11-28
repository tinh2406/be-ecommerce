from typing import List, Tuple

from products.models import (
    ProductAttribute,
    ProductAttributeValue,
    ProductAttributeVariant,
    ProductVariant,
)


class ProductAttributeService:

    @classmethod
    def create_multiple_attribute(
        cls, attributes: List[dict], product_id: int
    ) -> Tuple[List[ProductAttribute], dict]:

        created_attributes = dict()

        # Create product attributes
        product_attributes = ProductAttribute.objects.bulk_create(
            [
                ProductAttribute(name=attribute.get("name"), product_id=product_id)
                for attribute in attributes
            ]
        )

        # Create product attribute values
        product_attribute_values = []
        for attribute, attribute_values in zip(product_attributes, attributes):
            product_attributes_values_per_attribute = [
                ProductAttributeValue(attribute=attribute, value=value)
                for value in attribute_values["values"]
            ]

            product_attribute_values.extend(product_attributes_values_per_attribute)

        product_attribute_values = ProductAttributeValue.objects.bulk_create(
            product_attribute_values
        )

        for attribute_value in product_attribute_values:
            created_attributes[
                f"{attribute_value.attribute.name}_{attribute_value.value}"
            ] = attribute_value.id

        return product_attributes, created_attributes

    @classmethod
    def create_multiple_variants(
        cls, variants: List[dict], product_id: int, created_attributes: dict
    ) -> Tuple[List[ProductAttribute], dict]:

        # create product variants
        product_variants = ProductVariant.objects.bulk_create(
            [
                ProductVariant(
                    price=variant.pop("price"),
                    image=variant.pop("image"),
                    product_id=product_id,
                    hot_price=variant.pop("hot_price", None),
                )
                for variant in variants
            ]
        )

        product_variants_attributes = []
        for variant, variant_attributes in zip(product_variants, variants):
            for name, value in list(variant_attributes.items()):
                if f"{name}_{value}" not in created_attributes:
                    continue

                product_variants_attributes.append(
                    ProductAttributeVariant(
                        product_variant=variant,
                        product_attribute_value_id=created_attributes[
                            f"{name}_{value}"
                        ],
                    )
                )
        ProductAttributeVariant.objects.bulk_create(product_variants_attributes)

        return product_variants

    @classmethod
    def bulk_create(cls, validated_product, product_id, **kwargs):

        attributes = validated_product.get("attributes", None)
        variants = validated_product.get("variants", None)

        if not attributes or not variants:
            return [], []

        product_attributes, created_attributes = cls.create_multiple_attribute(
            attributes, product_id
        )
        product_variants = cls.create_multiple_variants(
            variants, product_id, created_attributes
        )

        return product_attributes, product_variants

    @classmethod
    def delete_multiple(cls, product_id):
        ProductAttribute.objects.filter(product_id=product_id).delete()
        ProductVariant.objects.filter(product_id=product_id).delete()
