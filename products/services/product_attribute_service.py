from products.models import ProductAttribute, ProductVariant


class ProductAttributeService:

    @classmethod
    def create_product_attribute(
        cls, name, values, product_id, **kwargs
    ) -> ProductAttribute:
        product_attribute = ProductAttribute.objects.create(
            name=name, product_id=product_id
        )
        for value in values:
            product_attribute.values.create(value=value)

        return product_attribute

    @classmethod
    def create_product_variant(
        cls, price, image, product_id, hot_price=None, **kwargs
    ) -> ProductVariant:
        product_variant = ProductVariant.objects.create(
            product_id=product_id, price=price, image=image, hot_price=hot_price
        )

        return product_variant

    @classmethod
    def create_multiple(cls, attributes, variants, product_id, **kwargs):
        product_attributes = dict()

        created_attributes = {}
        created_variants = []

        for attribute in attributes:
            product_attribute = cls.create_product_attribute(
                name=attribute.get("name"),
                values=attribute.get("values"),
                product_id=product_id,
            )
            product_attribute_values = product_attribute.values.all()

            created_attributes[product_attribute.name] = [
                attribute_value.value for attribute_value in product_attribute_values
            ]

            for attribute_value in product_attribute_values:
                product_attributes[
                    f"{product_attribute.name}_{attribute_value.value}"
                ] = attribute_value.id

        for variant in variants:
            product_variant = cls.create_product_variant(
                price=variant.pop("price"),
                image=variant.pop("image"),
                product_id=product_id,
                hot_price=variant.pop("hot_price", None),
            )
            for name, value in list(variant.items()):
                if f"{name}_{value}" not in product_attributes:
                    continue
                product_variant.attributes.create(
                    product_attribute_value_id=product_attributes[f"{name}_{value}"]
                )

            created_variants.append(
                {
                    "price": product_variant.price,
                    "image": product_variant.image,
                    "hot_price": product_variant.hot_price,
                    "attributes": {
                        attribute.product_attribute_value.attribute.name: attribute.product_attribute_value.value
                        for attribute in product_variant.attributes.all()
                    },
                }
            )

        return {"attributes": created_attributes, "variants": created_variants}

    @classmethod
    def delete_multiple(cls, product_id):
        ProductAttribute.objects.filter(product_id=product_id).delete()
        ProductVariant.objects.filter(product_id=product_id).delete()
