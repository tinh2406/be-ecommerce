import uuid

from django.db.models import (
    PROTECT,
    CharField,
    FloatField,
    ForeignKey,
    Manager,
    TextField,
    UUIDField,
)

from core.models import BaseTimeModel


class Item(BaseTimeModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(max_length=255)
    description = TextField(null=True)
    category = ForeignKey("items.Category", on_delete=PROTECT, related_name="items")
    price = FloatField()
    hot_price = FloatField(null=True)
    thumbnail = CharField(max_length=255)

    objects = Manager()
    key = "item_"
    cache_fields = ["id"]

    class Meta:
        db_table = "items"
