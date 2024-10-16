from uuid import uuid4

from django.db.models import PROTECT, CharField, ForeignKey, UUIDField

from core.models import BaseTimeModel


class Category(BaseTimeModel):

    id = UUIDField(primary_key=True, default=uuid4)
    name = CharField(max_length=255)

    parent = ForeignKey(
        "products.Category", null=True, on_delete=PROTECT, related_name="childs"
    )

    cache_key_fields = ["id"]
    key: str = "category_"

    class Meta:
        db_table = "categories"
