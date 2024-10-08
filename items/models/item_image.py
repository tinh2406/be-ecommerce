from uuid import uuid4

from django.db.models import CASCADE, CharField, ForeignKey, Manager, Model, UUIDField


class ItemImage(Model):
    id = UUIDField(primary_key=True, editable=False, default=uuid4)
    item = ForeignKey("items.Item", on_delete=CASCADE, related_name="images")
    url = CharField(max_length=255)

    objects = Manager()

    class Meta:
        db_table = "item_images"
