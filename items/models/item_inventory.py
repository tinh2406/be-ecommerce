from uuid import uuid4

from django.db.models import CASCADE, ForeignKey, IntegerField, Manager, UUIDField

from core.models import BaseTimeModel


class ItemInventory(BaseTimeModel):
    id = UUIDField(primary_key=True, default=uuid4)
    item = ForeignKey("items.Item", on_delete=CASCADE, related_name="inventories")

    before = IntegerField(default=0)
    after = IntegerField()
    quantity = IntegerField()

    key: str = "inventory_"
    cache_fields = ["id"]

    objects = Manager()

    class Meta:
        db_table = "item_inventories"
