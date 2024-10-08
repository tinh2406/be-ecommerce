from items.models import ItemAttribute, ItemVariant


class ItemAttributeService:

    @classmethod
    def create_item_attribute(cls, name, values, item_id, **kwargs) -> ItemAttribute:

        item_attribute = ItemAttribute.objects.create(name=name, item_id=item_id)
        for value in values:
            item_attribute.values.create(value=value)

        return item_attribute

    @classmethod
    def create_item_variant(
        cls, price, image, item_id, hot_price=None, **kwargs
    ) -> ItemVariant:

        item_variant = ItemVariant.objects.create(
            item_id=item_id, price=price, image=image, hot_price=hot_price
        )

        return item_variant

    @classmethod
    def create_multiple(cls, attributes, variants, item_id, **kwargs):
        item_attributes = dict()

        created_attributes = {}
        created_variants = []

        for attribute in attributes:
            item_attribute = cls.create_item_attribute(
                name=attribute.get("name"),
                values=attribute.get("values"),
                item_id=item_id,
            )
            item_attribute_values = item_attribute.values.all()

            created_attributes[item_attribute.name] = [
                attribute_value.value for attribute_value in item_attribute_values
            ]

            for attribute_value in item_attribute_values:
                item_attributes[f"{item_attribute.name}_{attribute_value.value}"] = (
                    attribute_value.id
                )

        for variant in variants:
            item_variant = cls.create_item_variant(
                price=variant.pop("price"),
                image=variant.pop("image"),
                item_id=item_id,
                hot_price=variant.pop("hot_price", None),
            )
            for name, value in list(variant.items()):
                if f"{name}_{value}" not in item_attributes:
                    continue
                item_variant.attributes.create(
                    item_attribute_value_id=item_attributes[f"{name}_{value}"]
                )

            created_variants.append(
                {
                    "price": item_variant.price,
                    "image": item_variant.image,
                    "hot_price": item_variant.hot_price,
                    "attributes": {
                        attribute.item_attribute_value.attribute.name: attribute.item_attribute_value.value
                        for attribute in item_variant.attributes.all()
                    },
                }
            )

        return {"attributes": created_attributes, "variants": created_variants}

    @classmethod
    def delete_multiple(cls, item_id):
        ItemAttribute.objects.filter(item_id=item_id).delete()
        ItemVariant.objects.filter(item_id=item_id).delete()
