from uuid import uuid4

from django.db.models import CASCADE, ForeignKey, Manager, Model, UUIDField


class ItemAttributeVariant(Model):

    id = UUIDField(primary_key=True, default=uuid4)
    item_variant = ForeignKey(
        "items.ItemVariant", on_delete=CASCADE, related_name="attributes"
    )
    item_attribute_value = ForeignKey(
        "items.ItemAttributeValue", on_delete=CASCADE, related_name="variants"
    )

    objects = Manager()

    class Meta:
        db_table = "item_attribute_variants"
