from uuid import uuid4

from django.db.models import CASCADE, CharField, ForeignKey, Manager, Model, UUIDField


class ItemAttribute(Model):
    id = UUIDField(primary_key=True, default=uuid4)
    item = ForeignKey("items.Item", on_delete=CASCADE, related_name="attributes")
    name = CharField(max_length=255)

    objects = Manager()

    class Meta:
        db_table = "item_attributes"
