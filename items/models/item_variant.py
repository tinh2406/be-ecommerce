from uuid import uuid4

from django.db.models import (
    CASCADE,
    CharField,
    DecimalField,
    ForeignKey,
    Manager,
    Model,
    UUIDField,
)


class ItemVariant(Model):
    id = UUIDField(primary_key=True, default=uuid4)
    price = DecimalField(max_digits=10, decimal_places=2)
    hot_price = DecimalField(max_digits=10, decimal_places=2, null=True)
    image = CharField(max_length=255, null=True)
    item = ForeignKey("items.Item", on_delete=CASCADE, related_name="variants")

    objects = Manager()

    class Meta:
        db_table = "item_variants"
