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


class Product(BaseTimeModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(max_length=255)
    description = TextField(null=True)
    category = ForeignKey(
        "products.Category", on_delete=PROTECT, related_name="products"
    )
    price = FloatField()
    hot_price = FloatField(null=True)
    thumbnail = CharField(max_length=255)

    objects = Manager()
    cache_key_fields = ["id"]
    cache_time = 300

    class Meta:
        db_table = "products"
