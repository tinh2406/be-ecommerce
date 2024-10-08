import pickle
import uuid

from django.core.cache import cache
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
from items.utils.representation_item import representation_item


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

    @classmethod
    def cache_load(cls, **kwargs):
        id = kwargs.get("id")
        key_cache = f"{cls.key}{id}"

        pickled_object = cache.get(key_cache)
        if pickled_object:
            obj = pickle.loads(pickled_object)
        else:
            obj = cls.objects.get(id=id)
            obj = representation_item(obj)
            pickled_object = pickle.dumps(obj)

        cache.set(key_cache, pickled_object, timeout=cls.cache_time)
        return obj
