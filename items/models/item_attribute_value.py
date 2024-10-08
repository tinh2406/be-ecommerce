from uuid import uuid4

from django.db.models import CASCADE, CharField, ForeignKey, Manager, Model, UUIDField


class ItemAttributeValue(Model):
    id = UUIDField(primary_key=True, default=uuid4)
    attribute = ForeignKey(
        "items.ItemAttribute", on_delete=CASCADE, related_name="values"
    )
    value = CharField(max_length=255)

    objects = Manager()

    class Meta:
        db_table = "item_attribute_values"
